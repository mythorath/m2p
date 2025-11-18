#!/usr/bin/env python3
"""Test script for the pool poller - runs a single polling cycle."""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.pool_poller import PoolPoller
from server.database import init_db
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run a single polling cycle for testing."""
    try:
        logger.info("Starting test polling cycle...")

        # Initialize database (create tables if needed)
        init_db()

        # Create poller (without SocketIO for testing)
        poller = PoolPoller(socketio_client=None)

        # Run a single polling cycle
        await poller.poll_all_players()

        # Print metrics
        metrics = poller.metrics.get_summary()
        logger.info("=" * 60)
        logger.info("POLLING METRICS:")
        logger.info(f"  Total polls: {metrics['polls_total']}")
        logger.info(f"  Successful: {metrics['polls_successful']}")
        logger.info(f"  Failed: {metrics['polls_failed']}")
        logger.info(f"  Rewards detected: {metrics['rewards_detected']}")
        logger.info("")
        logger.info("Per-pool statistics:")
        for pool_name, stats in metrics['pools'].items():
            logger.info(f"  {pool_name}:")
            logger.info(f"    Requests: {stats['requests']}")
            logger.info(f"    Success rate: {stats['success_rate']:.2%}")
            logger.info(f"    Avg response time: {stats['avg_response_time_ms']:.2f}ms")
        logger.info("=" * 60)

        logger.info("Test polling cycle complete!")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
