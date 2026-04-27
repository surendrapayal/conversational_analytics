import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from conversational_analytics.config import get_settings

cfg = get_settings()

logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

for noisy_logger in [
    "httpcore", "httpx", "urllib3", "asyncio",
    "langchain", "langchain_core", "langchain_community",
    "langchain_google_genai", "langchain_google_vertexai",
    "google", "google.auth", "google.api_core",
]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)

# All other imports after logging is configured
import uvicorn
from fastapi import FastAPI
from conversational_analytics.controller import router
from conversational_analytics.memory import setup_schema
from conversational_analytics.controller.agent_service import init_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async startup and shutdown lifecycle."""
    # ── Startup ───────────────────────────────────────────────────────
    logger.info("Application starting up...")

    # Run sync schema migration
    try:
        setup_schema()
    except Exception as e:
        logger.warning(f"Long-term memory schema setup failed: {e}")

    # Initialise async graph (AsyncRedisSaver + AsyncPostgresStore)
    await init_graph()
    logger.info("Application ready")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    logger.info("Application shutting down...")


app = FastAPI(
    title="Conversational Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)


if __name__ == "__main__":
    import selectors

    async def _serve():
        config = uvicorn.Config(app, host=cfg.app_host, port=cfg.app_port, reload=False)
        server = uvicorn.Server(config)
        await server.serve()

    if sys.platform == "win32":
        asyncio.run(_serve(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()))
    else:
        asyncio.run(_serve())
