from pathlib import Path
from pydantic import model_validator
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
    db_ignore_tables: str = ""       # comma-separated, empty = ignore none
    db_include_tables: str = ""      # comma-separated, empty = include all
    db_sample_rows_in_table_info: int = 3
    db_view_support: bool = False
    # Comma-separated table.column pairs to hide from the LLM
    db_restrict_columns: str = ""

    @property
    def db_restrict_columns_map(self) -> dict[str, list[str]]:
        """Returns {table: [col1, col2]} from DB_RESTRICT_COLUMNS=table.col1,table.col2."""
        result: dict[str, list[str]] = {}
        for entry in self.db_restrict_columns.split(","):
            entry = entry.strip()
            if "." not in entry:
                continue
            table, col = entry.split(".", 1)
            result.setdefault(table.strip(), []).append(col.strip())
        return result

    @property
    def db_ignore_tables_list(self) -> list[str]:
        return [t.strip() for t in self.db_ignore_tables.split(",") if t.strip()]

    @property
    def db_include_tables_list(self) -> list[str]:
        return [t.strip() for t in self.db_include_tables.split(",") if t.strip()]

    @model_validator(mode="after")
    def validate_table_filters(self) -> "Settings":
        if self.db_ignore_tables_list and self.db_include_tables_list:
            raise ValueError(
                "DB_IGNORE_TABLES and DB_INCLUDE_TABLES are mutually exclusive. "
                "Set only one of them in .env."
            )
        return self

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_session_ttl: int = 3600

    # App Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    agent_max_iterations: int = 10

    @property
    def db_uri(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
