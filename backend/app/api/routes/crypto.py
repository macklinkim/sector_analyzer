"""Crypto tab endpoints. All reads go against the daily-refreshed DB cache;
live price/volume is streamed directly to the browser from Binance WebSocket
and bypasses this API entirely."""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from app.agents.crypto_analyst import analyze_crypto_scores
from app.api.deps import get_settings, get_supabase
from app.config import Settings
from app.services.coingecko import TRACKED_COINS, fetch_coin_metadata
from app.services.crypto_news import fetch_crypto_news
from app.services.news_translator import translate_headlines
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


async def _run_crypto_pipeline(settings: Settings) -> dict:
    """crypto 일일 파이프라인 본체: metadata → news → AI scores.

    BackgroundTasks로 실행되므로 요청 스코프 의존성 대신 자체 SupabaseService를 생성.
    반환값은 로깅용(HTTP 응답에는 쓰이지 않음).
    """
    svc = SupabaseService(settings)

    # 1. Metadata (CoinGecko, 1 API call)
    try:
        meta_rows = await fetch_coin_metadata()
        svc.upsert_coin_metadata(meta_rows)
    except Exception as e:
        logger.error("CoinGecko fetch failed: %s", e, exc_info=True)
        meta_rows = svc.get_coin_metadata()  # fall back to stale cache for downstream steps

    # 2. News (RSS aggregation) + Korean one-sentence summary via Haiku
    symbols = [c["symbol"] for c in TRACKED_COINS]
    try:
        news_rows = await fetch_crypto_news(coin_symbols=symbols, limit=40)
        news_rows = translate_headlines(news_rows, settings)
        svc.upsert_coin_news(news_rows)
    except Exception as e:
        logger.error("Crypto news fetch failed: %s", e, exc_info=True)
        news_rows = svc.get_latest_coin_news(limit=40)

    # 3. AI scores (Claude)
    try:
        scores = analyze_crypto_scores(coins=meta_rows, news=news_rows, settings=settings)
        svc.insert_coin_ai_scores(scores)
    except Exception as e:
        logger.error("Crypto analyst failed: %s", e, exc_info=True)
        scores = []

    result = {
        "metadata_count": len(meta_rows),
        "news_count": len(news_rows),
        "scores_count": len(scores),
    }
    logger.info("crypto/trigger/daily finished: %s", result)
    return result


@router.post("/trigger/daily", status_code=202)
async def trigger_daily_crypto_batch(
    background_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
    x_trigger_key: Annotated[str | None, Header()] = None,
) -> dict:
    """crypto 일일 파이프라인을 백그라운드로 실행하고 즉시 202를 반환.

    파이프라인을 기다리지 않으므로 짧은 응답 타임아웃에도 안전.
    """
    if settings.trigger_api_key and x_trigger_key != settings.trigger_api_key:
        raise HTTPException(status_code=403, detail="Invalid trigger key")

    background_tasks.add_task(_run_crypto_pipeline, settings)
    logger.info("crypto/trigger/daily: accepted, pipeline running in background")
    return {"status": "accepted"}
