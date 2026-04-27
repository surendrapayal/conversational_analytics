import logging
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


async def get_checkpointer() -> AsyncRedisSaver | MemorySaver:
    """Returns a checkpointer based on SHORT_TERM_MEMORY_TYPE — redis or inmemory."""
    cfg = get_settings()
    if cfg.short_term_memory_type == "inmemory":
        return _get_inmemory_checkpointer()
    return await _get_redis_checkpointer(cfg)


def _get_inmemory_checkpointer() -> MemorySaver:
    """Returns a MemorySaver checkpointer — for local development only, not persistent."""
    logger.warning(
        "Short-term memory type is 'inmemory' — state is not persisted across restarts. "
        "Use 'redis' for production."
    )
    checkpointer = MemorySaver()
    logger.info("MemorySaver checkpointer initialised (inmemory short-term memory)")
    return checkpointer


async def _get_redis_checkpointer(cfg) -> AsyncRedisSaver:
    """Returns an AsyncRedisSaver checkpointer backed by Redis."""
    logger.info(f"Initialising AsyncRedisSaver checkpointer at {cfg.short_term_memory_url}...")
    try:
        checkpointer = AsyncRedisSaver(redis_url=cfg.short_term_memory_url)
        await checkpointer.asetup()
        logger.info(f"AsyncRedisSaver checkpointer initialised — ttl={cfg.short_term_memory_session_ttl}s")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialise Redis checkpointer at {cfg.short_term_memory_url}: {e}")
        raise
