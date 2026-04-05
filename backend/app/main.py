from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.news import router as news_router

app = FastAPI(
    title="Economi Analyzer API",
    description="AI-Driven Market Insights Dashboard - Sector Rotation Analysis",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(market_router)
app.include_router(news_router)


@app.get("/")
def root():
    return {
        "name": "Economi Analyzer API",
        "version": "0.1.0",
        "docs": "/docs",
    }
