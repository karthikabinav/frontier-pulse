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
