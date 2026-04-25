import logging
from langgraph.checkpoint.redis import RedisSaver
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


def get_checkpointer() -> RedisSaver:
    """Returns a RedisSaver checkpointer for LangGraph state persistence."""
    cfg = get_settings()
    logger.info(f"Initialising Redis checkpointer at {cfg.redis_url}...")
    try:
        checkpointer = RedisSaver(redis_url=cfg.redis_url)
        checkpointer.setup()
        logger.info("Redis checkpointer initialised (short-term memory)")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialise Redis checkpointer at {cfg.redis_url}: {e}")
        raise
