from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Resolves to the project root regardless of where the app is run from
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    google_cloud_project: str
    llm_model: str = "gemini-2.0-flash"
    llm_region: str = "us-east1"
    llm_temperature: float = 0.7
    llm_max_output_tokens: int = 2048
    llm_top_p: float = 0.9
    thinking_level: str = "medium"
    include_thoughts: bool = True

    # Database
    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "zenvyra"
    db_user: str = "admin_user"
    db_password: str = "admin_password"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_session_ttl: int = 3600

    # App Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    @property
    def db_uri(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
