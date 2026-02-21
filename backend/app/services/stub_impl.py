from app.config import settings
from app.schemas.domain import (
    InferencePolicyResponse,
    IngestionPolicyResponse,
    PaperSummary,
    ProjectPolicyResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)
from app.services.contracts import PaperService, WorkflowService


class InMemoryPaperService(PaperService):
    def __init__(self) -> None:
        self._papers: list[PaperSummary] = [
            PaperSummary(
                arxiv_id="2401.00001",
                title="Inference-Time Scaling in Reasoning Models",
                abstract="Placeholder seed paper used while ingestion adapters are being wired.",
            )
        ]

    def list_papers(self) -> list[PaperSummary]:
        return self._papers


class StubWorkflowService(WorkflowService):
    def run_weekly(self, payload: WorkflowRunRequest) -> WorkflowRunResponse:
        simulated_count = 120 if payload.max_papers == 0 else payload.max_papers
        return WorkflowRunResponse(
            status="stubbed",
            ingested_papers=simulated_count,
            extracted_alpha_cards=simulated_count,
            synthesized_hypotheses=12,
            notes=(
                "Scaffold complete. Next step: connect multi-source ingestion + extraction pipeline. "
                f"Requested sources: {', '.join(payload.sources)}"
            ),
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


paper_service = InMemoryPaperService()
workflow_service = StubWorkflowService()
