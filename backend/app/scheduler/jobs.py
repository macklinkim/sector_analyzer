import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agents.crypto_analyst import analyze_crypto_scores
from app.agents.graph import build_graph
from app.agents.state import create_initial_state
from app.api.deps import get_settings, get_supabase
from app.services.coingecko import TRACKED_COINS, fetch_coin_metadata
from app.services.crypto_news import fetch_crypto_news
from app.services.market_calendar import is_market_open_today
from app.services.news_translator import translate_headlines

logger = logging.getLogger(__name__)


def run_batch(batch_type: str) -> dict:
    if not is_market_open_today():
        logger.info("Market closed (weekend/NYSE holiday) — skipping %s batch", batch_type)
        return {"batch_type": batch_type, "status": "skipped", "reason": "market_closed"}

    logger.info("Starting %s batch at %s", batch_type, datetime.now(timezone.utc).isoformat())
    try:
        graph = build_graph()
        initial_state = create_initial_state(batch_type)
        result = asyncio.run(graph.ainvoke(initial_state))
        logger.info("Completed %s batch", batch_type)
        return result
    except Exception as e:
        logger.exception("Batch %s failed", batch_type)
        return {"batch_type": batch_type, "status": "failed", "error": str(e)}


async def _run_crypto_batch_async() -> dict:
    settings = get_settings()
    svc = get_supabase()

    try:
        meta_rows = await fetch_coin_metadata()
        svc.upsert_coin_metadata(meta_rows)
    except Exception:
        logger.exception("CoinGecko fetch failed")
        meta_rows = svc.get_coin_metadata()

    try:
        news_rows = await fetch_crypto_news(
            coin_symbols=[c["symbol"] for c in TRACKED_COINS],
            limit=40,
        )
        news_rows = translate_headlines(news_rows, settings)
        svc.upsert_coin_news(news_rows)
    except Exception:
        logger.exception("Crypto news fetch failed")
        news_rows = svc.get_latest_coin_news(limit=40)

    try:
        scores = analyze_crypto_scores(coins=meta_rows, news=news_rows, settings=settings)
        svc.insert_coin_ai_scores(scores)
    except Exception:
        logger.exception("Crypto analyst failed")
        scores = []

    return {
        "metadata_count": len(meta_rows),
        "news_count": len(news_rows),
        "scores_count": len(scores),
    }


def run_crypto_batch() -> dict:
    """Daily crypto pipeline — 24/7 market so no weekend/holiday skip."""
    logger.info("Starting crypto batch at %s", datetime.now(timezone.utc).isoformat())
    try:
        return asyncio.run(_run_crypto_batch_async())
    except Exception as e:
        logger.exception("Crypto batch failed")
        return {"status": "failed", "error": str(e)}


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="US/Eastern")

    # KST 17:30 = ET 04:30 (pre-market)
    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=4, minute=30, day_of_week="mon-fri", timezone="US/Eastern"),
        args=["pre_market"],
        id="pre_market_batch",
        name="pre_market_batch",
        replace_existing=True,
    )

    # US market open 09:30 + 1h = ET 10:30
    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=10, minute=30, day_of_week="mon-fri", timezone="US/Eastern"),
        args=["market_open"],
        id="market_open_batch",
        name="market_open_batch",
        replace_existing=True,
    )

    # US market close 16:00 + 1h = ET 17:00
    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=17, minute=0, day_of_week="mon-fri", timezone="US/Eastern"),
        args=["post_market"],
        id="post_market_batch",
        name="post_market_batch",
        replace_existing=True,
    )

    # Crypto: 24/7 market, daily at ET 00:00 (KST 13:00)
    scheduler.add_job(
        run_crypto_batch,
        trigger=CronTrigger(hour=0, minute=0, timezone="US/Eastern"),
        id="crypto_daily_batch",
        name="crypto_daily_batch",
        replace_existing=True,
    )

    return scheduler
