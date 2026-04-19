import logging
from langgraph.checkpoint.redis import RedisSaver
from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)


def get_checkpointer() -> RedisSaver:
    """Returns a RedisSaver checkpointer for LangGraph state persistence."""
    cfg = get_settings()
    checkpointer = RedisSaver(redis_url=cfg.redis_url)
    checkpointer.setup()  # creates required Redis index structures
    return checkpointer
