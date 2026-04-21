"""Crypto tab endpoints. All reads go against the daily-refreshed DB cache;
live price/volume is streamed directly to the browser from Binance WebSocket
and bypasses this API entirely."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.agents.crypto_analyst import analyze_crypto_scores
from app.api.deps import get_settings, get_supabase
from app.config import Settings
from app.services.coingecko import TRACKED_COINS, fetch_coin_metadata
from app.services.cryptopanic import fetch_crypto_news
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crypto", tags=["crypto"])


@router.get("/metadata")
def get_coin_metadata(svc: SupabaseService = Depends(get_supabase)) -> list[dict]:
    return svc.get_coin_metadata()


@router.get("/news")
def get_coin_news(
    limit: int = 30,
    svc: SupabaseService = Depends(get_supabase),
) -> list[dict]:
    return svc.get_latest_coin_news(limit=limit)


@router.get("/scores")
def get_coin_ai_scores(svc: SupabaseService = Depends(get_supabase)) -> list[dict]:
    return svc.get_latest_coin_ai_scores()


@router.post("/trigger/daily")
async def trigger_daily_crypto_batch(
    settings: Annotated[Settings, Depends(get_settings)],
    svc: Annotated[SupabaseService, Depends(get_supabase)],
    x_trigger_key: Annotated[str | None, Header()] = None,
) -> dict:
    """Run the full daily crypto pipeline: metadata → news → AI scores."""
    if settings.trigger_api_key and x_trigger_key != settings.trigger_api_key:
        raise HTTPException(status_code=403, detail="Invalid trigger key")

    # 1. Metadata (CoinGecko, 1 API call)
    try:
        meta_rows = await fetch_coin_metadata()
        svc.upsert_coin_metadata(meta_rows)
    except Exception as e:
        logger.error("CoinGecko fetch failed: %s", e, exc_info=True)
        meta_rows = svc.get_coin_metadata()  # fall back to stale cache for downstream steps

    # 2. News (CryptoPanic, 1 API call)
    symbols = [c["symbol"] for c in TRACKED_COINS]
    try:
        news_rows = await fetch_crypto_news(
            api_key=settings.cryptopanic_api_key,
            coin_symbols=symbols,
            limit=40,
        )
        svc.upsert_coin_news(news_rows)
    except Exception as e:
        logger.error("CryptoPanic fetch failed: %s", e, exc_info=True)
        news_rows = svc.get_latest_coin_news(limit=40)

    # 3. AI scores (Claude)
    try:
        scores = analyze_crypto_scores(coins=meta_rows, news=news_rows, settings=settings)
        svc.insert_coin_ai_scores(scores)
    except Exception as e:
        logger.error("Crypto analyst failed: %s", e, exc_info=True)
        scores = []

    return {
        "metadata_count": len(meta_rows),
        "news_count": len(news_rows),
        "scores_count": len(scores),
    }
