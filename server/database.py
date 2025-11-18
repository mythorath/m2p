"""
Database configuration and initialization for M2P
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.models import Base
import logging

logger = logging.getLogger(__name__)

# Default database URL
DATABASE_URL = 'sqlite:///./m2p.db'


def get_engine(database_url=None):
    """Create and return a database engine"""
    url = database_url or DATABASE_URL
    return create_engine(url, echo=False)


def get_session_factory(engine):
    """Create and return a session factory"""
    return sessionmaker(bind=engine)


def init_database(database_url=None):
    """
    Initialize the database by creating all tables.

    Args:
        database_url: Database connection string. If None, uses default.
    """
    engine = get_engine(database_url)

    logger.info("Initializing database...")
    Base.metadata.create_all(engine)
    logger.info("Database initialized successfully!")

    return engine


if __name__ == '__main__':
    # Run this to initialize the database
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("✅ Database initialized!")
