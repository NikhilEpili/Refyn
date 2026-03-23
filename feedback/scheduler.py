"""Daily APScheduler job for aggregating feedback."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from feedback.aggregator import compute_strictness_weights
import structlog

logger = structlog.get_logger()

def start_scheduler() -> AsyncIOScheduler:
    """Start the daily RLHF aggregation job."""
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        compute_strictness_weights,
        trigger=CronTrigger(hour=2, minute=0, timezone="UTC"),
        id="compute_strictness",
        name="RLHF Strictness Aggregation",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Started RLHF aggregation scheduler")
    return scheduler
