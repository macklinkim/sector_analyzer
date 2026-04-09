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


@router.get("/summaries")
def get_news_summaries(
    limit: int = Query(15, ge=1, le=50),
    svc: SupabaseService = Depends(get_supabase),
):
    """Get pre-computed AI news summaries from DB (generated during pipeline batch)."""
    return svc.get_latest_news_summaries(limit=limit)


@router.get("/crises")
def get_global_crises(svc: SupabaseService = Depends(get_supabase)):
    """Get pre-computed global crises from DB (generated during pipeline batch)."""
    return svc.get_latest_global_crises()
