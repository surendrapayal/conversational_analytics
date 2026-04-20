import logging
import psycopg2
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


def _get_connection():
    cfg = get_settings()
    return psycopg2.connect(
        host=cfg.db_host,
        port=cfg.db_port,
        database=cfg.db_name,
        user=cfg.db_user,
        password=cfg.db_password,
    )


def create_row_filter_views(role: str, row_filters: dict[str, str]) -> dict[str, str]:
    """Creates or replaces views for each table with a row filter.

    For each entry in row_filters {table: where_clause}:
      CREATE OR REPLACE VIEW v_<role>_<table> AS SELECT * FROM <table> WHERE <condition>

    Returns a mapping {original_table: view_name} for use in include_tables.
    """
    if not row_filters:
        return {}

    view_map: dict[str, str] = {}
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            for table, condition in row_filters.items():
                view_name = f"v_{role}_{table}"
                sql = f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM {table} WHERE {condition};"
                cur.execute(sql)
                view_map[table] = view_name
                logger.info(f"Created view '{view_name}' for role '{role}' with filter: {condition}")
        conn.commit()
    finally:
        conn.close()

    return view_map


def drop_row_filter_views(role: str, tables: list[str]) -> None:
    """Drops views created for a role. Called on shutdown or role reconfiguration."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            for table in tables:
                view_name = f"v_{role}_{table}"
                cur.execute(f"DROP VIEW IF EXISTS {view_name};")
                logger.info(f"Dropped view '{view_name}'")
        conn.commit()
    finally:
        conn.close()
