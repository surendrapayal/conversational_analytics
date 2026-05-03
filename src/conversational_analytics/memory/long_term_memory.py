import logging
import asyncio

from psycopg_pool import AsyncConnectionPool
from langgraph.store.postgres.aio import AsyncPostgresStore

from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)

_async_store: AsyncPostgresStore | None = None
_store_lock: asyncio.Lock | None = None


async def get_long_term_store() -> AsyncPostgresStore:
    """Returns AsyncPostgresStore with pgvector auto-embedding — async singleton."""
    global _async_store, _store_lock
    if _store_lock is None:
        _store_lock = asyncio.Lock()
    async with _store_lock:
        if _async_store is not None:
            return _async_store

        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        logger.info("Initialising AsyncPostgresStore with pgvector auto-embedding...")
        try:
            cfg = get_settings()
            embeddings = GoogleGenerativeAIEmbeddings(
                model=f"models/{cfg.embedding_model}",
                vertexai=True,
                project=cfg.google_cloud_project,
                location=cfg.llm_region,
            )
            logger.info(f"Embedding model: {cfg.embedding_model} ({cfg.embedding_dimension} dims)")

            pool = AsyncConnectionPool(
                cfg.long_term_memory_db_uri,
                min_size=1,
                max_size=10,
                kwargs={"autocommit": True, "prepare_threshold": 0},
                open=False,
            )
            await asyncio.wait_for(pool.open(wait=True), timeout=15.0)

            _async_store = AsyncPostgresStore(
                conn=pool,
                index={
                    "embed": embeddings,
                    "dims": cfg.embedding_dimension,
                    "fields": ["summary"],
                },
            )
            # Tables are pre-created by agent-memory-db-init.sql — skip setup() to avoid DDL lock.
            logger.info("AsyncPostgresStore initialised (pgvector auto-embedding)")
            return _async_store
        except Exception as e:
            logger.error(f"Failed to initialise AsyncPostgresStore: {e}", exc_info=True)
            raise


async def save_conversation_summary(
    user_id: str,
    session_id: str,
    conversation_id: str,
    user_query: str,
    response_text: str,
    role: str | None,
) -> None:
    """Saves conversation summary — AsyncPostgresStore auto-generates and stores embedding."""
    logger.debug(f"Saving conversation summary — user={user_id} conversation={conversation_id}")
    store = await get_long_term_store()
    summary = f"Q: {user_query[:150]} | A: {response_text[:300]}"
    try:
        await store.aput(
            ("conversation_summaries", user_id),
            conversation_id,
            {
                "summary": summary,
                "session_id": session_id,
                "conversation_id": conversation_id,
                "role": role,
            },
        )
        logger.info(f"Conversation summary + embedding saved — user={user_id} conversation={conversation_id}")
    except Exception as e:
        logger.error(f"Could not save conversation summary for user={user_id}: {e}", exc_info=True)


async def search_similar_conversations(
    user_id: str,
    query: str,
    limit: int = 3,
) -> list[dict]:
    """Semantic search over past conversation summaries using pgvector."""
    logger.debug(f"Semantic search for user={user_id} query='{query[:80]}' limit={limit}")
    store = await get_long_term_store()
    try:
        results = await store.asearch(
            ("conversation_summaries", user_id),
            query=query,
            limit=limit,
        )
        logger.debug(f"Raw asearch results count={len(results)} for user={user_id}")
        for r in results:
            logger.debug(f"  key={r.key} score={r.score} has_summary={bool(r.value.get('summary'))}")
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
        logger.warning(f"Semantic search failed for user={user_id}: {e}", exc_info=True)
        return []
