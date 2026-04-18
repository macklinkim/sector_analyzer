import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agents.graph import build_graph
from app.agents.state import create_initial_state
from app.services.market_calendar import is_market_open_today

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

    return scheduler
