import logging
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


async def get_checkpointer() -> AsyncRedisSaver:
    """Returns an AsyncRedisSaver checkpointer for LangGraph short-term state persistence."""
    cfg = get_settings()
    logger.info(f"Initialising AsyncRedisSaver checkpointer at {cfg.short_term_memory_url}...")
    try:
        checkpointer = AsyncRedisSaver(redis_url=cfg.short_term_memory_url)
        await checkpointer.asetup()
        logger.info(f"AsyncRedisSaver checkpointer initialised — ttl={cfg.short_term_memory_session_ttl}s")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialise Redis checkpointer at {cfg.short_term_memory_url}: {e}")
        raise
