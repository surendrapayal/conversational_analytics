from pathlib import Path
import os
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE, override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────
    google_cloud_project: str
    llm_model: str = "gemini-2.0-flash"
    llm_region: str = "us-east1"
    llm_temperature: float = 0.7
    llm_max_output_tokens: int = 2048
    llm_top_p: float = 0.9
    thinking_level: str = "medium"
    include_thoughts: bool = True

    # ── Analytics Database ────────────────────────────────────────────
    analytics_db_host: str = "localhost"
    analytics_db_port: int = 5433
    analytics_db_name: str = "zenvyra"
    analytics_db_user: str = "ca_agent_user"
    analytics_db_password: str = "ca_agent_password"
    db_ignore_tables: str = ""
    db_include_tables: str = ""
    db_sample_rows_in_table_info: int = 3
    db_view_support: bool = False
    db_restrict_columns: str = ""

    # ── Long-Term Memory Database (separate from analytics DB) ────────
    long_term_memory_db_host: str = "localhost"
    long_term_memory_db_port: int = 5433
    long_term_memory_db_name: str = "zenvyra"
    long_term_memory_db_user: str = "admin_user"
    long_term_memory_db_password: str = "admin_password"

    # ── Redis (short-term memory) ─────────────────────────────────────
    redis_url: str = "redis://localhost:6379"
    redis_session_ttl: int = 3600

    # ── App Server ────────────────────────────────────────────────────
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    agent_max_iterations: int = 10
    semantic_layer_path: str = ""
    log_prompt: bool = False

    # ── Embedding (pgvector semantic search) ─────────────────────────
    embedding_model: str = "text-embedding-005"
    embedding_dimension: int = 768
    memory_long_term_recall_limit: int = 3
    memory_short_term_message_limit: int = 0  # 0 = unlimited

    # ── Analytics DB properties ───────────────────────────────────────

    @property
    def db_uri(self) -> str:
        return f"postgresql+psycopg2://{self.analytics_db_user}:{self.analytics_db_password}@{self.analytics_db_host}:{self.analytics_db_port}/{self.analytics_db_name}"

    @property
    def db_restrict_columns_map(self) -> dict[str, list[str]]:
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

    # ── Memory DB properties ──────────────────────────────────────────

    @property
    def long_term_memory_db_uri(self) -> str:
        return f"postgresql://{self.long_term_memory_db_user}:{self.long_term_memory_db_password}@{self.long_term_memory_db_host}:{self.long_term_memory_db_port}/{self.long_term_memory_db_name}"

    @property
    def long_term_memory_db_dsn(self) -> dict:
        return {
            "host": self.long_term_memory_db_host,
            "port": self.long_term_memory_db_port,
            "dbname": self.long_term_memory_db_name,
            "user": self.long_term_memory_db_user,
            "password": self.long_term_memory_db_password,
        }

    # ── Role properties ───────────────────────────────────────────────

    @property
    def role_tables_map(self) -> dict[str, list[str]]:
        """Dynamically discovers all ROLE_<NAME>=tables entries from env vars."""
        result: dict[str, list[str]] = {}
        for key, value in os.environ.items():
            if not key.startswith("ROLE_"):
                continue
            if key.endswith("_RESTRICT_COLUMNS") or key.endswith("_ROW_FILTERS"):
                continue
            if not value.strip():
                continue
            role = key[len("ROLE_"):].lower()
            result[role] = [t.strip() for t in value.split(",") if t.strip()]
        return result

    def get_tables_for_role(self, role: str) -> list[str] | None:
        return self.role_tables_map.get(role.lower())

    def get_restrict_columns_for_role(self, role: str) -> dict[str, list[str]]:
        env_key = f"ROLE_{role.upper()}_RESTRICT_COLUMNS"
        raw = os.environ.get(env_key, "").strip() or self.db_restrict_columns
        result: dict[str, list[str]] = {}
        for entry in raw.split(","):
            entry = entry.strip()
            if "." not in entry:
                continue
            table, col = entry.split(".", 1)
            result.setdefault(table.strip(), []).append(col.strip())
        return result

    def get_row_filters_for_role(self, role: str) -> dict[str, str]:
        env_key = f"ROLE_{role.upper()}_ROW_FILTERS"
        raw = os.environ.get(env_key, "").strip()
        if not raw:
            return {}
        result: dict[str, str] = {}
        separator = "|" if "|" in raw else ","
        for entry in raw.split(separator):
            entry = entry.strip()
            if ":" not in entry:
                continue
            table, condition = entry.split(":", 1)
            result[table.strip()] = condition.strip()
        return result

    # ── Validators ────────────────────────────────────────────────────

    @model_validator(mode="after")
    def validate_table_filters(self) -> "Settings":
        if self.db_ignore_tables_list and self.db_include_tables_list:
            raise ValueError(
                "DB_IGNORE_TABLES and DB_INCLUDE_TABLES are mutually exclusive. "
                "Set only one of them in .env."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
