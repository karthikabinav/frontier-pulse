from app.config import settings
from app.schemas.domain import IngestionPolicyResponse, PaperSummary, WorkflowRunRequest, WorkflowRunResponse
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


paper_service = InMemoryPaperService()
workflow_service = StubWorkflowService()
