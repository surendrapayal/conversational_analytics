from pathlib import Path
import os
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv, find_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE, override=True)


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
    db_ignore_tables: str = ""
    db_include_tables: str = ""
    db_sample_rows_in_table_info: int = 3
    db_view_support: bool = False
    db_restrict_columns: str = ""

    # Role Based Access — dynamic, no hardcoded role fields
    # Any ROLE_<NAME>=tables and ROLE_<NAME>_RESTRICT_COLUMNS=cols in .env is picked up automatically

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_session_ttl: int = 3600

    # App Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    agent_max_iterations: int = 10

    # ── Database properties ───────────────────────────────────────────

    @property
    def db_uri(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

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

    # ── Role properties ───────────────────────────────────────────────

    @property
    def role_tables_map(self) -> dict[str, list[str]]:
        """Dynamically discovers all ROLE_<NAME>=tables entries from env vars.
        Excludes ROLE_<NAME>_RESTRICT_COLUMNS and ROLE_<NAME>_ROW_FILTERS entries.
        """
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
        """Returns allowed tables for a role, or None if role is not defined."""
        return self.role_tables_map.get(role.lower())

    def get_restrict_columns_for_role(self, role: str) -> dict[str, list[str]]:
        """Returns column restriction map for a role, falls back to global DB_RESTRICT_COLUMNS."""
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
        """Returns {table: where_clause} from ROLE_<NAME>_ROW_FILTERS=table:condition,...

        Format in .env:
          ROLE_LOCATION_MANAGER_ROW_FILTERS=orders:location_id=1,shifts:location_id=1

        The condition after ':' is used directly as a SQL WHERE clause.
        Use '|' as separator if a condition contains a comma:
          ROLE_LOCATION_MANAGER_ROW_FILTERS=orders:location_id=1|shifts:location_id=1
        """
        env_key = f"ROLE_{role.upper()}_ROW_FILTERS"
        raw = os.environ.get(env_key, "").strip()
        if not raw:
            return {}
        result: dict[str, str] = {}
        # support both comma and pipe as entry separator
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
