from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Frontier Pulse API"
    env: str = "dev"
    database_url: str = "postgresql+psycopg://frontier:frontier@localhost:5432/frontier_pulse"
    weekly_cron: str = "0 2 * * *"
    weekly_timezone: str = "America/Los_Angeles"
    default_max_papers: int = 0
    ingest_sources: str = "arxiv,openreview,frontier_blogs,x_threads,reddit,university_blogs"
    arxiv_categories: str = "cs.CL,cs.LG,stat.ML,cs.AI,cs.DS,cs.GT,cs.MA"
    include_revised_papers: bool = True
    dedupe_strategy: str = "fuzzy_title_abstract"
    pdf_parser_primary: str = "pymupdf"
    pdf_parser_fallback: str = "pdfminer"
    appendix_policy: str = "main_first_fallback"
    equation_policy: str = "plain_text_v1"
    chunk_target_tokens: int = 1200
    chunk_overlap_tokens: int = 150
    semantic_sectioning: bool = True
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b-instruct"
    llm_synthesis_model: str = "qwen2.5:7b-instruct"
    llm_temperature: float = 0.35
    llm_enable_cloud_fallback: bool = True
    llm_fallback_provider: str = "openrouter"
    llm_weekly_budget_usd: float = 5.0
    llm_weekly_max_calls: int = 600
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_api_key: str = ""
    embedding_model: str = "nomic-embed-text"
    embedding_scope: str = "chunks_and_paper"
    vector_metadata_filters: bool = True
    alpha_card_versioning: str = "immutable_with_history"
    novelty_score_mode: str = "ordinal"
    hypothesis_strength_mode: str = "model_with_human_override"
    contradiction_edges_enabled: bool = True
    citation_provenance_required: bool = True
    auth_required: bool = False
    cluster_edit_mode: str = "v1_1"
    hypothesis_user_rating_scale: str = "binary"
    hotkeys_enabled: bool = True
    editor_mode: str = "markdown"
    export_twitter_mode: str = "classic_thread"
    export_linkedin_tone: str = "founder_voice"
    export_include_visuals: bool = False
    export_template_mode: str = "shared_v1"
    export_delivery_mode: str = "clipboard"
    deployment_mode: str = "local_only"
    db_backend: str = "postgres"
    dev_runtime_mode: str = "native_first"
    scheduler_mode: str = "in_process"
    backup_retention_days: int = 7
    min_acceptable_precision: float = 0.70
    manual_qa_checklist: bool = True
    track_model_drift: bool = False
    benchmark_set_required: bool = True
    primary_success_metric: str = "output_quality"
    redact_export_paths: bool = True
    db_encryption_at_rest: bool = False
    first_real_weekly_run_date: str = "2026-02-23"

    @property
    def ingest_sources_list(self) -> list[str]:
        return [item.strip() for item in self.ingest_sources.split(",") if item.strip()]

    @property
    def arxiv_categories_list(self) -> list[str]:
        return [item.strip() for item in self.arxiv_categories.split(",") if item.strip()]


settings = Settings()
