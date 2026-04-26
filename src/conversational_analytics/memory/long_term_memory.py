import logging
import psycopg2
import psycopg2.pool
import psycopg2.extras
from pathlib import Path
from functools import lru_cache

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from langgraph.store.postgres import PostgresStore

from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_long_term_store() -> PostgresStore:
    """Returns PostgresStore with pgvector auto-embedding via store.put().

    Passes GoogleGenerativeAIEmbeddings (Vertex AI, ADC) to the index config.
    LangGraph automatically:
    1. Extracts the 'summary' field from the value dict
    2. Calls text-embedding-005 to generate a 768-dim vector
    3. Stores JSONB value + VECTOR embedding in a single INSERT
    """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    logger.info("Initialising long-term PostgresStore with pgvector auto-embedding...")
    try:
        cfg = get_settings()

        # ── 1. Embedding model (ADC via Vertex AI — no API key needed) ─
        embeddings = GoogleGenerativeAIEmbeddings(
            model=f"models/{cfg.embedding_model}",
            vertexai=True,
            project=cfg.google_cloud_project,
            location=cfg.llm_region,
        )
        logger.info(f"Embedding model: {cfg.embedding_model} ({cfg.embedding_dimension} dims)")

        # ── 2. Connection pool ────────────────────────────────────────
        pool = ConnectionPool(
            cfg.long_term_memory_db_uri,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
            open=True,
        )

        # ── 3. Store with pgvector index config ───────────────────────
        # 'fields' = which JSONB keys to embed — only meaningful text fields
        # store.put() will concatenate these fields and call embed automatically
        store = PostgresStore(
            conn=pool,
            index={
                "embed": embeddings,
                "dims": cfg.embedding_dimension,
                "fields": ["summary"],  # embed the summary field only
            },
        )

        # ── 4. Creates store table + vector column + HNSW index ───────
        store.setup()
        logger.info("Long-term memory store initialised (PostgresStore + pgvector auto-embedding)")
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
    """Saves conversation summary using store.put() — LangGraph auto-generates
    and stores the embedding for the 'summary' field in a single operation.

    Flow:
      store.put(value={"summary": "Q: ... | A: ..."})
        → LangGraph extracts "summary" field (configured in index.fields)
        → calls VertexAI text-embedding-005 → 768-dim vector
        → INSERT INTO public.store (prefix, key, value, embedding) in one shot
    """
    logger.debug(f"Saving conversation summary — user={user_id} conversation={conversation_id}")
    store = get_long_term_store()
    summary = f"Q: {user_query[:150]} | A: {response_text[:300]}"
    try:
        store.put(
            ("conversation_summaries", user_id),
            conversation_id,
            {
                "summary": summary,          # ← this field gets auto-embedded
                "session_id": session_id,
                "conversation_id": conversation_id,
                "role": role,
            },
        )
        logger.info(f"Conversation summary + embedding saved — user={user_id} conversation={conversation_id}")
    except Exception as e:
        logger.warning(f"Could not save conversation summary for user={user_id}: {e}")


def search_similar_conversations(
    user_id: str,
    query: str,
    limit: int = 3,
) -> list[dict]:
    """Semantic search over past conversation summaries using pgvector.

    LangGraph store.search() automatically:
    1. Embeds the query string using the configured embedding model
    2. Queries store_vectors table for cosine similarity
    3. Returns results ordered by similarity score
    """
    logger.debug(f"Semantic search for user={user_id} query='{query[:80]}' limit={limit}")
    store = get_long_term_store()
    try:
        results = store.search(
            ("conversation_summaries", user_id),
            query=query,
            limit=limit,
        )
        formatted = [
            {
                "conversation_id": r.key,
                "summary": r.value.get("summary", ""),
                "role": r.value.get("role"),
                "session_id": r.value.get("session_id"),
                "similarity": r.score,
            }
            for r in results
            if r.value.get("summary")
        ]
        logger.info(f"Semantic search returned {len(formatted)} results for user={user_id}")
        return formatted
    except Exception as e:
        logger.warning(f"Semantic search failed for user={user_id}: {e}")
        return []


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
    logger.debug(f"Logging query — user={user_id} conversation={conversation_id} tools={tools_invoked} has_vega={has_vega} execution_ms={execution_ms}")
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
        logger.info(f"Query logged — user={user_id} conversation={conversation_id} execution_ms={execution_ms} has_vega={has_vega}")
        if token_usage:
            logger.info(f"Token usage — input={token_usage.get('input_tokens',0)} output={token_usage.get('output_tokens',0)} total={token_usage.get('total_tokens',0)}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to log query for conversation={conversation_id}: {e}")
        raise
    finally:
        pool.putconn(conn)
