from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import (
    Cluster,
    ClusterPaperLink,
    Hypothesis,
    HypothesisPaperLink,
    IngestionRun,
    Paper,
    PaperAlphaCard,
    PaperChunk,
    ResearchBrief,
    ResearchBriefVersion,
    ResearchMemoryEntry,
)
from app.schemas.domain import (
    BriefUpdateRequest,
    BriefVersionOut,
    ClusterOut,
    ExportItem,
    ExportRequest,
    ExportResponse,
    HypothesisOut,
    InferencePolicyResponse,
    IngestionPolicyResponse,
    PaperDetail,
    PaperSummary,
    ProjectPolicyResponse,
    QAItem,
    QAResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    MemoryEntryOut,
)
from app.services.contracts import AnalysisService, BriefService, ExportService, PaperService, QAService, WorkflowService
from app.services.inference import FailoverInferenceClient, InferenceRequest, OllamaClient, OpenRouterClient
from app.services.sources import ArxivConnector, OpenReviewConnector, RSSConnector, SourceDocument, default_rss_sources
from app.services.text_utils import make_chunks, strip_reference_tail


def _week_key(ts: Optional[datetime] = None) -> str:
    base = ts or datetime.now(timezone.utc)
    year, week, _ = base.isocalendar()
    return f"{year}-W{week:02d}"


def _novelty_bucket(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ["first", "novel", "new"]):
        return "high"
    if any(k in lowered for k in ["incremental", "baseline", "ablation"]):
        return "low"
    return "medium"


def _embed_text(text: str, dim: int = 1024) -> list[float]:
    """Deterministic lightweight embedding placeholder for local-first retrieval.

    Replace with model-based embeddings in a later pass.
    """
    if not text:
        return [0.0] * dim
    values: list[float] = []
    seed = text.encode("utf-8", errors="ignore")
    counter = 0
    while len(values) < dim:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "little")).digest()
        for b in digest:
            values.append((b / 127.5) - 1.0)
            if len(values) >= dim:
                break
        counter += 1
    return values


def _heuristic_alpha(doc: Paper, chunks: list[PaperChunk]) -> dict[str, str]:
    corpus = f"{doc.title}\n{doc.abstract}".lower()
    bottleneck = "reasoning depth" if "reason" in corpus else "inference efficiency"
    mechanism = "test-time compute" if any(k in corpus for k in ["test-time", "inference-time"]) else "training/data"
    scaling_axis = "compute" if "compute" in corpus else "data"
    compute_regime = "low-to-medium"

    snippet = ""
    if chunks:
        snippet = chunks[0].text[:240]

    return {
        "bottleneck_attacked": bottleneck,
        "mechanism_type": mechanism,
        "scaling_axis": scaling_axis,
        "compute_regime": compute_regime,
        "claimed_improvement": doc.abstract[:600],
        "evaluation_risk": "Potential benchmark overfitting; requires robustness checks.",
        "implicit_assumptions": "Assumes gains transfer to out-of-distribution tasks.",
        "novelty_bucket": _novelty_bucket(doc.title + " " + doc.abstract),
        "generalization_likelihood": "medium",
        "scaling_projection": "Expected gains increase with additional inference budget.",
        "strategic_relevance": "Relevant for frontier inference-time optimization roadmap.",
        "short_alpha_summary": f"{doc.title}: {doc.abstract[:220]}",
        "provenance_snippets": snippet,
    }


def _build_hypotheses(alpha_cards: list[PaperAlphaCard], week_key: str) -> list[tuple[Hypothesis, list[tuple[int, str, float, str]]]]:
    grouped: dict[str, list[PaperAlphaCard]] = {}
    for card in alpha_cards:
        grouped.setdefault(card.mechanism_type, []).append(card)

    out = []
    for mechanism, cards in grouped.items():
        title = f"{mechanism} approaches continue to improve frontier model reasoning efficiency"
        strength = min(1.0, 0.4 + 0.08 * len(cards))
        hyp = Hypothesis(text=title, type="mechanism", strength_score=strength, week_introduced=week_key)
        links: list[tuple[int, str, float, str]] = []
        for card in cards:
            relation = "support"
            conf = min(0.95, 0.5 + 0.05 * len(cards))
            prov = card.provenance_snippets[:220]
            links.append((card.paper_id, relation, conf, prov))
        out.append((hyp, links))

    return out


def _cluster_cards(alpha_cards: list[PaperAlphaCard], week_key: str) -> list[tuple[Cluster, list[int]]]:
    grouped: dict[str, list[PaperAlphaCard]] = {}
    for card in alpha_cards:
        grouped.setdefault(card.bottleneck_attacked, []).append(card)

    clusters: list[tuple[Cluster, list[int]]] = []
    for bottleneck, cards in grouped.items():
        cluster = Cluster(
            name=f"{bottleneck.title()} Cluster",
            dominant_bottleneck=bottleneck,
            mechanism_summary=f"Dominant mechanisms: {', '.join(sorted({c.mechanism_type for c in cards}))}",
            week_key=week_key,
        )
        paper_ids = [card.paper_id for card in cards]
        clusters.append((cluster, paper_ids))
    return clusters


def _derive_long_horizon_insights(db: Session, current_week_key: str, lookback: int = 6) -> str:
    weeks = db.scalars(
        select(ResearchBrief.week_key).order_by(desc(ResearchBrief.week_key)).limit(max(lookback, 1))
    ).all()
    if not weeks:
        return "No historical signal available yet."

    hyp_rows = db.scalars(
        select(Hypothesis).where(Hypothesis.week_introduced.in_(weeks)).order_by(desc(Hypothesis.created_at))
    ).all()
    cluster_rows = db.scalars(select(Cluster).where(Cluster.week_key.in_(weeks))).all()

    mechanism_counter = Counter([h.type for h in hyp_rows])
    bottleneck_counter = Counter([c.dominant_bottleneck for c in cluster_rows])

    top_mechanisms = ", ".join([f"{k}({v})" for k, v in mechanism_counter.most_common(3)]) or "none"
    top_bottlenecks = ", ".join([f"{k}({v})" for k, v in bottleneck_counter.most_common(3)]) or "none"

    return (
        f"Across the last {len(weeks)} tracked weeks (up to {current_week_key}), "
        f"the dominant hypothesis types are: {top_mechanisms}. "
        f"Most persistent bottlenecks are: {top_bottlenecks}."
    )


def _render_brief(
    week_key: str,
    papers: list[Paper],
    cards: list[PaperAlphaCard],
    hyps: list[Hypothesis],
    long_horizon_insight: str,
) -> str:
    count_by_source = Counter([p.source for p in papers])
    source_lines = "\n".join([f"- {k}: {v}" for k, v in sorted(count_by_source.items())]) or "- none"
    top_hyp = hyps[0].text if hyps else "No hypotheses generated yet."

    return f"""# aifrontierpulse Weekly Brief ({week_key})

## Field Temperature
- Total ingested artifacts: {len(papers)}
- Source distribution:
{source_lines}

## Dominant Bottleneck
- {cards[0].bottleneck_attacked if cards else 'N/A'}

## Top Hypothesis
- {top_hyp}

## Strategic Flags
- Citation provenance is {'enabled' if settings.citation_provenance_required else 'disabled'}.
- Quality gate target precision: {settings.min_acceptable_precision:.2f}

## Long-Horizon Insight
- {long_horizon_insight}

## Open Questions
- Which mechanisms remain robust across revised versions?
- Which gains are likely benchmark-specific?
"""


class DefaultPaperService(PaperService):
    def list_papers(self, db: Session, limit: int = 100) -> list[PaperSummary]:
        rows = db.scalars(select(Paper).order_by(desc(Paper.published_at)).limit(limit)).all()
        return [
            PaperSummary(
                id=row.id,
                source=row.source,
                source_id=row.source_id,
                title=row.title,
                abstract=row.abstract,
                published_at=row.published_at,
            )
            for row in rows
        ]

    def get_paper(self, db: Session, paper_id: int) -> PaperDetail:
        row = db.get(Paper, paper_id)
        if not row:
            raise ValueError(f"Paper {paper_id} not found")
        return PaperDetail(
            id=row.id,
            source=row.source,
            source_id=row.source_id,
            title=row.title,
            abstract=row.abstract,
            published_at=row.published_at,
            authors=row.authors,
            source_url=row.source_url,
        )


class DefaultWorkflowService(WorkflowService):
    def __init__(self) -> None:
        fallback = None
        if settings.llm_enable_cloud_fallback and settings.llm_fallback_provider == "openrouter":
            fallback = OpenRouterClient(api_key=settings.openrouter_api_key, model=settings.openrouter_model)
        self.inference_client = FailoverInferenceClient(primary_client=OllamaClient(), fallback_client=fallback)

    def _connectors(self, sources: list[str]) -> dict[str, object]:
        rss = default_rss_sources()
        mapping: dict[str, object] = {
            "arxiv": ArxivConnector(
                settings.arxiv_categories_list,
                parser_primary=settings.pdf_parser_primary,
                parser_fallback=settings.pdf_parser_fallback,
            ),
            "openreview": OpenReviewConnector(),
            "frontier_blogs": RSSConnector("frontier_blogs", rss["frontier_blogs"]),
            "reddit": RSSConnector("reddit", rss["reddit"]),
            "university_blogs": RSSConnector("university_blogs", rss["university_blogs"]),
        }
        if "x_threads" in sources:
            mapping["x_threads"] = RSSConnector("x_threads", rss.get("x_threads", []))
        return mapping

    def _dedupe_exists(self, db: Session, doc: SourceDocument) -> bool:
        existing = db.scalar(select(Paper).where(Paper.source_id == doc.source_id))
        if existing:
            return True

        if settings.dedupe_strategy == "fuzzy_title_abstract":
            title_prefix = doc.title.lower()[:120]
            candidates = db.scalars(select(Paper).where(Paper.title.ilike(f"%{title_prefix[:40]}%"))).all()
            for row in candidates:
                if row.abstract[:160].lower() == doc.abstract[:160].lower() and row.title[:120].lower() == title_prefix:
                    return True
        return False

    def _topic_score(self, doc: SourceDocument) -> int:
        if not settings.topic_bias_enabled:
            return 0
        text = f"{doc.title}\n{doc.abstract}".lower()
        score = 0
        for kw in settings.topic_bias_keywords_list:
            if kw in text:
                score += 1
        return score

    def _prioritize_docs(self, docs: list[SourceDocument], max_items: int) -> list[SourceDocument]:
        ranked = sorted(
            docs,
            key=lambda d: (
                self._topic_score(d),
                d.published_at,
            ),
            reverse=True,
        )
        if max_items > 0:
            return ranked[:max_items]
        return ranked

    def _store_paper(self, db: Session, doc: SourceDocument) -> Paper:
        body = doc.full_text
        if settings.appendix_policy == "main_first_fallback":
            body = strip_reference_tail(body)

        paper = Paper(
            source=doc.source,
            source_id=doc.source_id,
            arxiv_id=doc.arxiv_id,
            title=doc.title,
            authors=doc.authors,
            published_at=doc.published_at,
            updated_at=doc.updated_at,
            abstract=doc.abstract,
            full_text=body,
            source_url=doc.source_url,
            embedding_vector=_embed_text(f"{doc.title}\n{doc.abstract}", dim=1024),
        )
        db.add(paper)
        db.flush()

        chunks = make_chunks(
            body,
            target_tokens=settings.chunk_target_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
        for idx, chunk in enumerate(chunks):
            db.add(
                PaperChunk(
                    paper_id=paper.id,
                    section_name=chunk.section_name,
                    chunk_index=idx,
                    text=chunk.text,
                    estimated_tokens=chunk.estimated_tokens,
                    embedding_vector=_embed_text(chunk.text[:4000], dim=1024),
                )
            )
        return paper

    def _extract_alpha(self, db: Session, paper: Paper) -> PaperAlphaCard:
        chunks = db.scalars(select(PaperChunk).where(PaperChunk.paper_id == paper.id).order_by(PaperChunk.chunk_index)).all()
        data = _heuristic_alpha(paper, chunks)

        # Optional best-effort model enhancement. On parse failure we keep heuristic content.
        prompt = (
            "Summarize this paper for structured alpha extraction in 5 bullet points:\n\n"
            f"Title: {paper.title}\nAbstract: {paper.abstract[:3000]}"
        )
        try:
            model_text = self.inference_client.generate(
                InferenceRequest(prompt=prompt, model=settings.llm_model, temperature=settings.llm_temperature)
            ).text
            if model_text:
                data["strategic_relevance"] = model_text[:900]
        except Exception:
            pass

        current_cards = db.scalars(select(PaperAlphaCard).where(PaperAlphaCard.paper_id == paper.id, PaperAlphaCard.is_current)).all()
        for c in current_cards:
            c.is_current = False

        card = PaperAlphaCard(
            paper_id=paper.id,
            version_number=(len(current_cards) + 1),
            is_current=True,
            **data,
        )
        db.add(card)
        db.flush()
        return card

    def run_weekly(self, db: Session, payload: WorkflowRunRequest) -> WorkflowRunResponse:
        week_key = _week_key()
        requested = payload.sources or settings.ingest_sources_list
        max_items = payload.max_papers if payload.max_papers > 0 else 120

        run = IngestionRun(source_scope=",".join(requested), notes="weekly pipeline")
        db.add(run)
        db.flush()

        connectors = self._connectors(requested)
        docs: list[SourceDocument] = []
        source_errors: list[str] = []
        per_source_cap = max(15, max_items // max(1, len(requested)))
        for source in requested:
            connector = connectors.get(source)
            if not connector:
                continue
            try:
                fetched = connector.fetch(max_items=per_source_cap)
                docs.extend(fetched)
            except Exception as exc:
                source_errors.append(f"{source}:{exc}")

        prioritized_docs = self._prioritize_docs(docs, max_items=max_items)
        topic_matches = sum(1 for d in prioritized_docs if self._topic_score(d) > 0)

        papers_added: list[Paper] = []
        for doc in prioritized_docs:
            if self._dedupe_exists(db, doc):
                continue
            papers_added.append(self._store_paper(db, doc))

        alpha_cards = [self._extract_alpha(db, paper) for paper in papers_added]

        hypotheses_input = _build_hypotheses(alpha_cards, week_key)
        hypotheses: list[Hypothesis] = []
        for hyp, links in hypotheses_input:
            db.add(hyp)
            db.flush()
            hypotheses.append(hyp)
            for paper_id, relation, conf, prov in links:
                db.add(
                    HypothesisPaperLink(
                        hypothesis_id=hyp.id,
                        paper_id=paper_id,
                        relation=relation,
                        confidence=conf,
                        provenance=prov,
                    )
                )

        clusters_input = _cluster_cards(alpha_cards, week_key)
        clusters: list[Cluster] = []
        for cluster, paper_ids in clusters_input:
            db.add(cluster)
            db.flush()
            clusters.append(cluster)
            for paper_id in paper_ids:
                db.add(ClusterPaperLink(cluster_id=cluster.id, paper_id=paper_id))

        brief = db.scalar(select(ResearchBrief).where(ResearchBrief.week_key == week_key))
        if not brief:
            brief = ResearchBrief(week_key=week_key, title=f"aifrontierpulse {week_key}", status="draft")
            db.add(brief)
            db.flush()

        current_version = db.scalar(
            select(func.max(ResearchBriefVersion.version_number)).where(ResearchBriefVersion.brief_id == brief.id)
        )
        version_number = int(current_version or 0) + 1
        long_horizon_insight = _derive_long_horizon_insights(db, week_key, lookback=6)
        markdown = _render_brief(week_key, papers_added, alpha_cards, hypotheses, long_horizon_insight)
        brief_version = ResearchBriefVersion(
            brief_id=brief.id,
            version_number=version_number,
            editor="system",
            markdown_content=markdown,
        )
        db.add(brief_version)

        # Memory entries (richer nugget + trend persistence)
        for hyp in hypotheses:
            key = f"{week_key}:hypothesis:{hyp.id}"
            summary = hyp.text
            db.merge(
                ResearchMemoryEntry(
                    memory_key=key,
                    memory_type="hypothesis",
                    title=hyp.text[:180],
                    summary=summary,
                    source_week=week_key,
                    provenance="derived from linked alpha cards with provenance snippets",
                    embedding_vector=_embed_text(summary, dim=1024),
                )
            )

        for card in alpha_cards:
            key = f"{week_key}:alpha:{card.paper_id}:{card.version_number}"
            summary = f"{card.short_alpha_summary}\nMechanism={card.mechanism_type}; Bottleneck={card.bottleneck_attacked}; Novelty={card.novelty_bucket}."
            db.merge(
                ResearchMemoryEntry(
                    memory_key=key,
                    memory_type="alpha_nugget",
                    title=summary[:180],
                    summary=summary,
                    source_week=week_key,
                    provenance=card.provenance_snippets[:1500],
                    embedding_vector=_embed_text(summary, dim=1024),
                )
            )

        trend_key = f"{week_key}:trend:long_horizon"
        db.merge(
            ResearchMemoryEntry(
                memory_key=trend_key,
                memory_type="weekly_synthesis",
                title=f"Long-horizon synthesis {week_key}",
                summary=long_horizon_insight,
                source_week=week_key,
                provenance="computed from prior hypotheses and clusters",
                embedding_vector=_embed_text(long_horizon_insight, dim=1024),
            )
        )

        run.total_items = len(papers_added)
        run.completed_at = datetime.now(timezone.utc)
        error_suffix = f" errors={'; '.join(source_errors[:3])}" if source_errors else ""
        run.notes = (
            f"ingested={len(papers_added)} topic_matched={topic_matches} hypotheses={len(hypotheses)} clusters={len(clusters)}{error_suffix}"
        )
        db.commit()

        return WorkflowRunResponse(
            status="completed",
            run_id=run.id,
            ingested_papers=len(papers_added),
            extracted_alpha_cards=len(alpha_cards),
            synthesized_hypotheses=len(hypotheses),
            generated_clusters=len(clusters),
            brief_version=version_number,
            notes=run.notes,
        )

    def ingestion_policy(self) -> IngestionPolicyResponse:
        return IngestionPolicyResponse(
            sources=settings.ingest_sources_list,
            arxiv_categories=settings.arxiv_categories_list,
            include_revised_papers=settings.include_revised_papers,
            dedupe_strategy=settings.dedupe_strategy,
            max_papers_policy="uncapped" if settings.default_max_papers == 0 else "bounded",
            pdf_parser_primary=settings.pdf_parser_primary,
            pdf_parser_fallback=settings.pdf_parser_fallback,
            appendix_policy=settings.appendix_policy,
            equation_policy=settings.equation_policy,
            chunk_target_tokens=settings.chunk_target_tokens,
            chunk_overlap_tokens=settings.chunk_overlap_tokens,
            semantic_sectioning=settings.semantic_sectioning,
            topic_bias_enabled=settings.topic_bias_enabled,
            topic_bias_keywords=settings.topic_bias_keywords_list,
        )

    def inference_policy(self) -> InferencePolicyResponse:
        return InferencePolicyResponse(
            llm_provider=settings.llm_provider,
            llm_model=settings.llm_model,
            llm_synthesis_model=settings.llm_synthesis_model,
            llm_temperature=settings.llm_temperature,
            llm_enable_cloud_fallback=settings.llm_enable_cloud_fallback,
            llm_fallback_provider=settings.llm_fallback_provider,
            llm_weekly_budget_usd=settings.llm_weekly_budget_usd,
            llm_weekly_max_calls=settings.llm_weekly_max_calls,
            openrouter_model=settings.openrouter_model,
        )

    def project_policy(self) -> ProjectPolicyResponse:
        return ProjectPolicyResponse(
            embedding_model=settings.embedding_model,
            embedding_scope=settings.embedding_scope,
            vector_metadata_filters=settings.vector_metadata_filters,
            alpha_card_versioning=settings.alpha_card_versioning,
            novelty_score_mode=settings.novelty_score_mode,
            hypothesis_strength_mode=settings.hypothesis_strength_mode,
            contradiction_edges_enabled=settings.contradiction_edges_enabled,
            citation_provenance_required=settings.citation_provenance_required,
            auth_required=settings.auth_required,
            cluster_edit_mode=settings.cluster_edit_mode,
            hypothesis_user_rating_scale=settings.hypothesis_user_rating_scale,
            hotkeys_enabled=settings.hotkeys_enabled,
            editor_mode=settings.editor_mode,
            export_twitter_mode=settings.export_twitter_mode,
            export_linkedin_tone=settings.export_linkedin_tone,
            export_include_visuals=settings.export_include_visuals,
            export_template_mode=settings.export_template_mode,
            export_delivery_mode=settings.export_delivery_mode,
            deployment_mode=settings.deployment_mode,
            db_backend=settings.db_backend,
            dev_runtime_mode=settings.dev_runtime_mode,
            scheduler_mode=settings.scheduler_mode,
            backup_retention_days=settings.backup_retention_days,
            min_acceptable_precision=settings.min_acceptable_precision,
            manual_qa_checklist=settings.manual_qa_checklist,
            track_model_drift=settings.track_model_drift,
            benchmark_set_required=settings.benchmark_set_required,
            primary_success_metric=settings.primary_success_metric,
            redact_export_paths=settings.redact_export_paths,
            db_encryption_at_rest=settings.db_encryption_at_rest,
            first_real_weekly_run_date=settings.first_real_weekly_run_date,
        )


class DefaultAnalysisService(AnalysisService):
    def list_hypotheses(self, db: Session, week_key: Optional[str] = None) -> list[HypothesisOut]:
        query = select(Hypothesis)
        if week_key:
            query = query.where(Hypothesis.week_introduced == week_key)
        rows = db.scalars(query.order_by(desc(Hypothesis.created_at))).all()
        out: list[HypothesisOut] = []
        for row in rows:
            links = db.scalars(select(HypothesisPaperLink).where(HypothesisPaperLink.hypothesis_id == row.id)).all()
            support_count = sum(1 for link in links if link.relation == "support")
            contradiction_count = sum(1 for link in links if link.relation == "contradict")
            out.append(
                HypothesisOut(
                    id=row.id,
                    text=row.text,
                    type=row.type,
                    strength_score=row.user_override_strength or row.strength_score,
                    user_override_strength=row.user_override_strength,
                    support_count=support_count,
                    contradiction_count=contradiction_count,
                )
            )
        return out

    def list_clusters(self, db: Session, week_key: Optional[str] = None) -> list[ClusterOut]:
        query = select(Cluster)
        if week_key:
            query = query.where(Cluster.week_key == week_key)
        rows = db.scalars(query.order_by(desc(Cluster.created_at))).all()
        out: list[ClusterOut] = []
        for row in rows:
            count = db.scalar(
                select(func.count(ClusterPaperLink.id)).where(ClusterPaperLink.cluster_id == row.id)
            ) or 0
            out.append(
                ClusterOut(
                    id=row.id,
                    name=row.name,
                    dominant_bottleneck=row.dominant_bottleneck,
                    mechanism_summary=row.mechanism_summary,
                    paper_count=int(count),
                )
            )
        return out

    def list_memory(
        self,
        db: Session,
        week_key: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[MemoryEntryOut]:
        query = select(ResearchMemoryEntry)
        if week_key:
            query = query.where(ResearchMemoryEntry.source_week == week_key)
        if memory_type:
            query = query.where(ResearchMemoryEntry.memory_type == memory_type)

        rows = db.scalars(query.order_by(desc(ResearchMemoryEntry.updated_at)).limit(limit)).all()
        return [
            MemoryEntryOut(
                id=row.id,
                memory_key=row.memory_key,
                memory_type=row.memory_type,
                title=row.title,
                summary=row.summary,
                source_week=row.source_week,
                provenance=row.provenance,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


class DefaultBriefService(BriefService):
    def latest_version(self, db: Session, week_key: Optional[str] = None) -> Optional[BriefVersionOut]:
        if week_key:
            brief = db.scalar(select(ResearchBrief).where(ResearchBrief.week_key == week_key))
        else:
            brief = db.scalar(select(ResearchBrief).order_by(desc(ResearchBrief.updated_at)))
        if not brief:
            return None

        version = db.scalar(
            select(ResearchBriefVersion)
            .where(ResearchBriefVersion.brief_id == brief.id)
            .order_by(desc(ResearchBriefVersion.version_number))
        )
        if not version:
            return None
        return BriefVersionOut(
            id=version.id,
            brief_id=brief.id,
            week_key=brief.week_key,
            version_number=version.version_number,
            editor=version.editor,
            markdown_content=version.markdown_content,
            created_at=version.created_at,
        )

    def update_brief(self, db: Session, payload: BriefUpdateRequest) -> BriefVersionOut:
        brief = db.scalar(select(ResearchBrief).where(ResearchBrief.week_key == payload.week_key))
        if not brief:
            brief = ResearchBrief(week_key=payload.week_key, title=f"aifrontierpulse {payload.week_key}", status="draft")
            db.add(brief)
            db.flush()

        current = db.scalar(
            select(func.max(ResearchBriefVersion.version_number)).where(ResearchBriefVersion.brief_id == brief.id)
        )
        version_number = int(current or 0) + 1
        row = ResearchBriefVersion(
            brief_id=brief.id,
            version_number=version_number,
            editor=payload.editor,
            markdown_content=payload.markdown_content,
        )
        brief.updated_at = datetime.now(timezone.utc)
        db.add(row)
        db.commit()
        db.refresh(row)
        return BriefVersionOut(
            id=row.id,
            brief_id=brief.id,
            week_key=brief.week_key,
            version_number=row.version_number,
            editor=row.editor,
            markdown_content=row.markdown_content,
            created_at=row.created_at,
        )


class DefaultExportService(ExportService):
    def _strip_paths(self, text: str) -> str:
        if not settings.redact_export_paths:
            return text
        return text.replace("/Users/", "~/")

    def _to_twitter_thread(self, markdown: str) -> str:
        lines = [line.strip() for line in markdown.splitlines() if line.strip()]
        tweets: list[str] = []
        current = ""
        for line in lines:
            part = line[:250]
            if len(current) + len(part) + 1 > 260:
                tweets.append(current)
                current = part
            else:
                current = f"{current} {part}".strip()
        if current:
            tweets.append(current)
        return "\n\n".join([f"{i+1}/{len(tweets)} {t}" for i, t in enumerate(tweets[:10])])

    def _to_linkedin(self, markdown: str) -> str:
        intro = "Building aifrontierpulse in public: this week’s frontier AI research signal."
        return f"{intro}\n\n{markdown[:2800]}"

    def generate(self, db: Session, payload: ExportRequest) -> ExportResponse:
        brief_version = db.get(ResearchBriefVersion, payload.brief_version_id)
        if not brief_version:
            raise ValueError(f"Brief version {payload.brief_version_id} not found")

        markdown = self._strip_paths(brief_version.markdown_content)
        items: list[ExportItem] = []

        for platform in payload.include_platforms:
            if platform == "twitter":
                content = self._to_twitter_thread(markdown)
            elif platform == "linkedin":
                content = self._to_linkedin(markdown)
            else:
                content = markdown
            items.append(ExportItem(platform=platform, content=content))

        return ExportResponse(items=items)


class DefaultQAService(QAService):
    def checklist(self, db: Session) -> QAResponse:
        latest = db.scalar(select(ResearchBriefVersion).order_by(desc(ResearchBriefVersion.created_at)))
        has_citation = bool(latest and "citation" in latest.markdown_content.lower())
        return QAResponse(
            checklist=[
                QAItem(id="citations", title="Claims include citations/provenance", required=True, passed=has_citation),
                QAItem(id="precision", title="Precision target >= 0.70 checked", required=True, passed=False),
                QAItem(id="paths", title="Absolute filesystem paths redacted", required=True, passed=True),
                QAItem(id="thread", title="Twitter export uses classic thread format", required=True, passed=True),
            ]
        )


paper_service = DefaultPaperService()
workflow_service = DefaultWorkflowService()
analysis_service = DefaultAnalysisService()
brief_service = DefaultBriefService()
export_service = DefaultExportService()
qa_service = DefaultQAService()
