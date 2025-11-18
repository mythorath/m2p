#!/usr/bin/env python3
"""Initialize the database by creating all tables."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.database import init_db, engine
from server.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    try:
        logger.info("Initializing database...")
        logger.info(f"Database URL: {engine.url}")

        # Create all tables
        init_db()

        logger.info("Database initialized successfully!")
        logger.info("Tables created:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  - {table.name}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
