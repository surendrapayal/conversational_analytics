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


def save_conversation_summary(
    user_id: str,
    session_id: str,
    conversation_id: str,
    user_query: str,
    response_text: str,
    role: str | None,
) -> None:
    """Writes a distilled conversation summary to the long-term store.

    Stored under namespace ('conversation_summaries', user_id) keyed by conversation_id.
    Each conversation gets its own entry — multiple conversations per session are preserved.
    """
    store = get_long_term_store()
    summary = f"Q: {user_query[:150]} | A: {response_text[:300]}"
    try:
        store.put(
            ("conversation_summaries", user_id),
            conversation_id,
            {
                "summary": summary,
                "session_id": session_id,
                "conversation_id": conversation_id,
                "role": role,
            },
        )
        logger.info(f"Saved conversation summary for user={user_id} session={session_id} conversation={conversation_id}")
    except Exception as e:
        logger.warning(f"Could not save conversation summary: {e}")


def log_agent_step(
    conversation_id: str,
    session_id: str,
    user_id: str,
    step_number: int,
    step_type: str,
    tool_name: str | None = None,
    input: str | None = None,
    output: str | None = None,
    token_usage: dict | None = None,
    duration_ms: int | None = None,
) -> None:
    """Logs a single ReAct agent step to memory.agent_steps.

    step_type values:
      llm_call    — LLM was invoked (thinking + tool decision or final response)
      tool_call   — a tool was called with args
      tool_result — a tool returned a result
    """
    import json as _json
    pool = _get_audit_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory.agent_steps
                    (conversation_id, session_id, user_id, step_number, step_type,
                     tool_name, input, output, token_usage, duration_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id, session_id, user_id, step_number, step_type,
                tool_name, input, output,
                _json.dumps(token_usage) if token_usage else None,
                duration_ms,
            ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def log_query(
    session_id: str,
    user_id: str,
    conversation_id: str,
    role: str | None,
    user_query: str,
    prompt: str | None,
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
                    (conversation_id, session_id, user_id, role, user_query, prompt,
                     sql_generated, tools_invoked, agent_response, vega_spec,
                     token_usage, has_vega, execution_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id, session_id, user_id, role, user_query, prompt,
                sql_generated, tools_invoked, agent_response,
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
