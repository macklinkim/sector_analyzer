import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.news import router as news_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.scheduler.jobs import create_scheduler

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started with jobs: %s", [j.name for j in scheduler.get_jobs()])
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


app = FastAPI(
    title="Economi Analyzer API",
    description="AI-Driven Market Insights Dashboard - Sector Rotation Analysis",
    version="0.1.0",
    lifespan=lifespan,
)

def _get_cors_origins() -> list[str]:
    from app.config import Settings
    origins = ["http://localhost:3000", "http://localhost:5173"]
    extra = Settings().cors_origins
    if extra:
        origins.extend([o.strip() for o in extra.split(",") if o.strip()])
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(market_router)
app.include_router(news_router)
app.include_router(analysis_router)


@app.get("/")
def root() -> dict:
    return {
        "name": "Economi Analyzer API",
        "version": "0.1.0",
        "docs": "/docs",
        "frontend": "https://sectoranalyzerfrontend2026.kopserf.workers.dev",
    }
