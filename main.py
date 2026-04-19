import logging
import uvicorn
from fastapi import FastAPI
from conversational_analytics.controller import router
from conversational_analytics.config import get_settings

cfg = get_settings()
logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Conversational Analytics API", version="1.0.0")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=cfg.app_host, port=cfg.app_port, reload=True)
