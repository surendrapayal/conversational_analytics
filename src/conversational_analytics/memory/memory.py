import logging
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


async def get_checkpointer() -> AsyncRedisSaver:
    """Returns an AsyncRedisSaver checkpointer for LangGraph state persistence."""
    cfg = get_settings()
    logger.info(f"Initialising AsyncRedisSaver checkpointer at {cfg.redis_url}...")
    try:
        checkpointer = AsyncRedisSaver(redis_url=cfg.redis_url)
        await checkpointer.asetup()
        logger.info("AsyncRedisSaver checkpointer initialised (short-term memory)")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialise Redis checkpointer at {cfg.redis_url}: {e}")
        raise
