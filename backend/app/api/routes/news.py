from fastapi import APIRouter, Depends, Query

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/articles")
def get_news_articles(
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    svc: SupabaseService = Depends(get_supabase),
):
    if category:
        return svc.get_news_by_category(category, limit=limit)
    return svc.get_latest_news_articles(limit=limit)


@router.get("/impacts")
def get_news_impacts(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_news_impacts()
