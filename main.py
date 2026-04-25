import logging
from conversational_analytics.config import get_settings

# Configure logging FIRST — before any imports that trigger module-level code
cfg = get_settings()
logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# All other imports after logging is configured
import uvicorn
from fastapi import FastAPI
from conversational_analytics.controller import router
from conversational_analytics.memory import setup_schema

# initialise long-term memory schema on startup
try:
    setup_schema()
except Exception as e:
    logging.getLogger(__name__).warning(f"Long-term memory schema setup failed: {e}")

app = FastAPI(title="Conversational Analytics API", version="1.0.0")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=cfg.app_host, port=cfg.app_port, reload=True)
