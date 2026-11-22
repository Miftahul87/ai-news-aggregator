from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "sqlite:///./news.db"
    cors_origins: str = "http://localhost:5173"
    ingest_timeout_seconds: float = 12
    ingest_max_articles_per_feed: int = 40
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
