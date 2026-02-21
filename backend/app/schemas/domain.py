from typing import Literal

from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    arxiv_id: str
    title: str
    abstract: str


class WorkflowRunRequest(BaseModel):
    max_papers: int = Field(default=0, ge=0)
    sources: list[
        Literal["arxiv", "openreview", "frontier_blogs", "x_threads", "reddit", "university_blogs"]
    ] = Field(default_factory=lambda: ["arxiv"])
    include_revised_papers: bool = True


class WorkflowRunResponse(BaseModel):
    status: str
    ingested_papers: int
    extracted_alpha_cards: int
    synthesized_hypotheses: int
    notes: str


class IngestionPolicyResponse(BaseModel):
    sources: list[str]
    arxiv_categories: list[str]
    include_revised_papers: bool
    dedupe_strategy: str
    max_papers_policy: str
    pdf_parser_primary: str
    pdf_parser_fallback: str
    appendix_policy: str
    equation_policy: str
    chunk_target_tokens: int
    chunk_overlap_tokens: int
    semantic_sectioning: bool


class InferencePolicyResponse(BaseModel):
    llm_provider: str
    llm_model: str
    llm_synthesis_model: str
    llm_temperature: float
    llm_enable_cloud_fallback: bool
    llm_fallback_provider: str
    llm_weekly_budget_usd: float
    llm_weekly_max_calls: int
    openrouter_model: str


class ProjectPolicyResponse(BaseModel):
    embedding_model: str
    embedding_scope: str
    vector_metadata_filters: bool
    alpha_card_versioning: str
    novelty_score_mode: str
    hypothesis_strength_mode: str
    contradiction_edges_enabled: bool
    citation_provenance_required: bool
    auth_required: bool
    cluster_edit_mode: str
    hypothesis_user_rating_scale: str
    hotkeys_enabled: bool
    editor_mode: str
    export_twitter_mode: str
    export_linkedin_tone: str
    export_include_visuals: bool
    export_template_mode: str
    export_delivery_mode: str
    deployment_mode: str
    db_backend: str
    dev_runtime_mode: str
    scheduler_mode: str
    backup_retention_days: int
    min_acceptable_precision: float
    manual_qa_checklist: bool
    track_model_drift: bool
    benchmark_set_required: bool
    primary_success_metric: str
    redact_export_paths: bool
    db_encryption_at_rest: bool
    first_real_weekly_run_date: str
