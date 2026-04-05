# backend/app/models/news.py
from datetime import datetime
from pydantic import BaseModel


class NewsArticle(BaseModel):
    category: str
    title: str
    source: str
    url: str
    summary: str | None = None
    published_at: datetime
    collected_at: datetime


class NewsImpactAnalysis(BaseModel):
    news_url: str
    sector_name: str
    impact_score: float
    impact_direction: str
    reasoning: str
    rotation_relevance: float = 0.0
    batch_type: str
    analyzed_at: datetime
