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
    logger.info("Initialising long-term PostgresStore connection pool...")
    try:
        pool = ConnectionPool(
            get_settings().long_term_memory_db_uri,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
            open=True,
        )
        store = PostgresStore(conn=pool)
        store.setup()
        logger.info("Long-term memory store initialised (PostgresStore with pool min=1 max=10)")
        return store
    except Exception as e:
        logger.error(f"Failed to initialise long-term memory store: {e}")
        raise


@lru_cache
def _get_audit_pool() -> psycopg2.pool.ThreadedConnectionPool:
    """Shared psycopg2 connection pool for audit log writes."""
    logger.debug("Creating psycopg2 audit connection pool (min=1 max=5)...")
    try:
        cfg = get_settings()
        pool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=5, **cfg.long_term_memory_db_dsn)
        logger.info("Audit connection pool created")
        return pool
    except Exception as e:
        logger.error(f"Failed to create audit connection pool: {e}")
        raise


def setup_schema() -> None:
    """Creates the memory schema, views and audit tables if they do not exist."""
    sql_file = Path(__file__).parent / "migrations" / "001_long_term_memory.sql"
    logger.info(f"Running memory schema migration from {sql_file}")
    cfg = get_settings()
    conn = psycopg2.connect(**cfg.long_term_memory_db_dsn)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql_file.read_text(encoding="utf-8"))
        logger.info("Long-term memory schema initialised successfully")
    except Exception as e:
        logger.error(f"Memory schema migration failed: {e}")
        raise
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
    """Writes a distilled conversation summary to the long-term store."""
    logger.debug(f"Saving conversation summary — user={user_id} session={session_id} conversation={conversation_id}")
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
        logger.info(f"Conversation summary saved — user={user_id} session={session_id} conversation={conversation_id}")
    except Exception as e:
        logger.warning(f"Could not save conversation summary for user={user_id} conversation={conversation_id}: {e}")


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
    """Logs a single ReAct agent step to memory.agent_steps."""
    import json as _json
    logger.debug(f"Logging agent step — conversation={conversation_id} step={step_number} type={step_type} tool={tool_name}")
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
        logger.debug(f"Agent step logged — step={step_number} type={step_type} duration={duration_ms}ms")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to log agent step {step_number} for conversation={conversation_id}: {e}")
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
    stream_events: list[dict] | None = None,
    has_vega: bool = False,
    execution_ms: int | None = None,
) -> None:
    """Writes a query audit record to memory.query_log using the connection pool."""
    import json as _json
    logger.debug(f"Logging query — user={user_id} session={session_id} conversation={conversation_id} tools={tools_invoked} has_vega={has_vega} execution_ms={execution_ms} stream_events={len(stream_events) if stream_events else 0}")
    pool = _get_audit_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memory.query_log
                    (conversation_id, session_id, user_id, role, user_query, prompt,
                     sql_generated, tools_invoked, agent_response, vega_spec,
                     token_usage, stream_events, has_vega, execution_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id, session_id, user_id, role, user_query, prompt,
                sql_generated, tools_invoked, agent_response,
                _json.dumps(vega_spec) if vega_spec else None,
                _json.dumps(token_usage) if token_usage else None,
                _json.dumps(stream_events) if stream_events else None,
                has_vega, execution_ms,
            ))
        conn.commit()
        logger.info(f"Query logged — user={user_id} conversation={conversation_id} execution_ms={execution_ms} has_vega={has_vega} stream_events={len(stream_events) if stream_events else 0}")
        if token_usage:
            logger.info(f"Token usage — input={token_usage.get('input_tokens',0)} output={token_usage.get('output_tokens',0)} total={token_usage.get('total_tokens',0)} reasoning={token_usage.get('reasoning_tokens',0)}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to log query for conversation={conversation_id}: {e}")
        raise
    finally:
        pool.putconn(conn)
