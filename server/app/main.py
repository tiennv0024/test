import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.tracks import router as tracks_router
from app.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    started = time.perf_counter()
    init_db()
    logger.info("Server startup completed in %.3f seconds", time.perf_counter() - started)
    yield


app = FastAPI(
    title="Eureka Music API",
    description="FastAPI backend for the Eureka Music desktop application.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(tracks_router)
