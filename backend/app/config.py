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

    @property
    def ingest_sources_list(self) -> list[str]:
        return [item.strip() for item in self.ingest_sources.split(",") if item.strip()]

    @property
    def arxiv_categories_list(self) -> list[str]:
        return [item.strip() for item in self.arxiv_categories.split(",") if item.strip()]


settings = Settings()
