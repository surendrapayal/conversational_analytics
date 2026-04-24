import logging
import time
from pathlib import Path
from functools import lru_cache

import psycopg2
import psycopg2.pool
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from langgraph.store.postgres import PostgresStore

from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_long_term_store() -> PostgresStore:
    """Returns the LangGraph PostgresStore using a connection pool — cached singleton."""
    pool = ConnectionPool(
        get_settings().memory_db_uri,
        min_size=1,
        max_size=10,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        open=True,
    )
    store = PostgresStore(conn=pool)
    store.setup()  # creates public.store table managed by LangGraph
    logger.info("Long-term memory store initialised (PostgresStore)")
    return store


@lru_cache
def _get_audit_pool() -> psycopg2.pool.ThreadedConnectionPool:
    """Shared psycopg2 connection pool for audit log writes."""
    cfg = get_settings()
    return psycopg2.pool.ThreadedConnectionPool(
        minconn=1, maxconn=5, **cfg.memory_db_dsn
    )


def setup_schema() -> None:
    """Creates the memory schema, views and audit tables if they do not exist."""
    sql_file = Path(__file__).parent / "migrations" / "001_long_term_memory.sql"
    cfg = get_settings()
    conn = psycopg2.connect(**cfg.memory_db_dsn)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql_file.read_text(encoding="utf-8"))
        logger.info("Long-term memory schema initialised")
    finally:
        conn.close()


def log_query(
    session_id: str,
    user_id: str,
    role: str | None,
    user_query: str,
    sql_generated: str | None,
    tools_invoked: list[str],
    has_vega: bool = False,
    execution_ms: int | None = None,
) -> None:
    """Writes a query audit record to memory.query_log using the connection pool."""
    pool = _get_audit_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory.query_log
                    (session_id, user_id, role, user_query, sql_generated,
                     tools_invoked, has_vega, execution_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, user_id, role, user_query, sql_generated,
                  tools_invoked, has_vega, execution_ms))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
