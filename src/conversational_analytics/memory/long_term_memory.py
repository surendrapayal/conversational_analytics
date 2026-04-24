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


def save_session_summary(
    user_id: str,
    session_id: str,
    user_query: str,
    response_text: str,
    role: str | None,
) -> None:
    """Writes a distilled session summary to the long-term store.

    Stored under namespace ('session_summaries', user_id) keyed by session_id.
    This is what gets recalled in future sessions to give the LLM cross-session context.

    Example stored value:
        {
            'summary': 'User asked about top 3 menu items. Answer: Spring Rolls (230)...',
            'session_id': 'session_001',
            'role': 'admin',
        }
    """
    store = get_long_term_store()
    # Truncate response to keep summary concise — first 300 chars is enough for context
    summary = f"Q: {user_query[:150]} | A: {response_text[:300]}"
    try:
        store.put(
            ("session_summaries", user_id),
            session_id,
            {"summary": summary, "session_id": session_id, "role": role},
        )
        logger.info(f"Saved session summary for user={user_id} session={session_id}")
    except Exception as e:
        logger.warning(f"Could not save session summary: {e}")


def log_query(
    session_id: str,
    user_id: str,
    role: str | None,
    user_query: str,
    sql_generated: str | None,
    tools_invoked: list[str],
    agent_response: str | None = None,
    vega_spec: dict | None = None,
    token_usage: dict | None = None,
    has_vega: bool = False,
    execution_ms: int | None = None,
) -> None:
    """Writes a query audit record to memory.query_log using the connection pool."""
    import json as _json
    pool = _get_audit_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory.query_log
                    (session_id, user_id, role, user_query, sql_generated,
                     tools_invoked, agent_response, vega_spec, token_usage,
                     has_vega, execution_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session_id, user_id, role, user_query, sql_generated,
                tools_invoked, agent_response,
                _json.dumps(vega_spec) if vega_spec else None,
                _json.dumps(token_usage) if token_usage else None,
                has_vega, execution_ms,
            ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
