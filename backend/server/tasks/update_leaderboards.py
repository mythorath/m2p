"""Background task for updating leaderboard cache."""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from server.leaderboard import LeaderboardManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_all_leaderboards():
    """Update all leaderboard caches."""
    db = SessionLocal()
    try:
        logger.info("Starting leaderboard cache update...")
        start_time = datetime.utcnow()

        # Get leaderboard manager
        manager = LeaderboardManager(db)

        # Update all periods
        update_counts = manager.update_leaderboard_cache()

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Log results
        logger.info(f"Leaderboard cache updated in {duration:.2f}s")
        for period, count in update_counts.items():
            logger.info(f"  {period}: {count} entries")

    except Exception as e:
        logger.error(f"Error updating leaderboard cache: {e}", exc_info=True)
    finally:
        db.close()


def start_leaderboard_scheduler(interval_minutes: int = 5):
    """Start background scheduler for leaderboard updates.

    Args:
        interval_minutes: Update interval in minutes
    """
    scheduler = BackgroundScheduler()

    # Schedule leaderboard updates
    scheduler.add_job(
        update_all_leaderboards,
        'interval',
        minutes=interval_minutes,
        id='update_leaderboards',
        name='Update leaderboard cache',
        replace_existing=True
    )

    # Run immediately on startup
    scheduler.add_job(
        update_all_leaderboards,
        'date',
        run_date=datetime.now(),
        id='update_leaderboards_startup',
        name='Initial leaderboard cache update'
    )

    scheduler.start()
    logger.info(f"Leaderboard scheduler started (interval: {interval_minutes} minutes)")

    return scheduler
