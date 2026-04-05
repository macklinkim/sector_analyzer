import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agents.graph import build_graph
from app.agents.state import create_initial_state

logger = logging.getLogger(__name__)


def run_batch(batch_type: str) -> dict:
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

    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=8, minute=30, timezone="US/Eastern"),
        args=["pre_market"],
        id="pre_market_batch",
        name="pre_market_batch",
        replace_existing=True,
    )

    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=17, minute=0, timezone="US/Eastern"),
        args=["post_market"],
        id="post_market_batch",
        name="post_market_batch",
        replace_existing=True,
    )

    return scheduler
