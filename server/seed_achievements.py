"""
Seeding script to populate the Achievement table with all achievements.
This script is idempotent - it can be run multiple times safely.
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.models import Base, Achievement
from server.achievements_data import ACHIEVEMENTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_achievements(database_url: str = None):
    """
    Seed the achievements table with all achievement definitions.

    Args:
        database_url: Database connection string. If None, uses default SQLite.
    """
    # Default to SQLite if no URL provided
    if database_url is None:
        database_url = 'sqlite:///./m2p.db'

    logger.info(f"Connecting to database: {database_url}")

    # Create engine and session
    engine = create_engine(database_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create all tables if they don't exist
        Base.metadata.create_all(engine)
        logger.info("Database tables created/verified")

        # Track statistics
        added_count = 0
        updated_count = 0
        skipped_count = 0

        # Process each achievement
        for achievement_data in ACHIEVEMENTS:
            # Check if achievement already exists
            existing = session.query(Achievement).filter(
                Achievement.achievement_id == achievement_data['id']
            ).first()

            if existing:
                # Update existing achievement
                updated = False
                for key, value in achievement_data.items():
                    if key == 'id':
                        continue  # Don't update the ID field

                    # Map 'id' to 'achievement_id' in the model
                    model_key = 'achievement_id' if key == 'id' else key

                    # Check if field has is_hidden, if not in data, default to False
                    if model_key == 'is_hidden' and 'is_hidden' not in achievement_data:
                        value = False

                    # Check if value changed
                    current_value = getattr(existing, model_key, None)
                    if current_value != value:
                        setattr(existing, model_key, value)
                        updated = True

                if updated:
                    updated_count += 1
                    logger.info(f"Updated achievement: {achievement_data['name']}")
                else:
                    skipped_count += 1
            else:
                # Create new achievement
                achievement = Achievement(
                    achievement_id=achievement_data['id'],
                    name=achievement_data['name'],
                    description=achievement_data['description'],
                    icon=achievement_data['icon'],
                    ap_reward=achievement_data['ap_reward'],
                    condition_type=achievement_data['condition_type'],
                    condition_value=achievement_data['condition_value'],
                    category=achievement_data.get('category', 'general'),
                    sort_order=achievement_data.get('sort_order', 0),
                    is_hidden=achievement_data.get('is_hidden', False)
                )
                session.add(achievement)
                added_count += 1
                logger.info(f"Added achievement: {achievement_data['name']}")

        # Commit all changes
        session.commit()

        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("ACHIEVEMENT SEEDING COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Total achievements in data: {len(ACHIEVEMENTS)}")
        logger.info(f"Added: {added_count}")
        logger.info(f"Updated: {updated_count}")
        logger.info(f"Skipped (no changes): {skipped_count}")
        logger.info("=" * 50)

        # Verify count in database
        total_in_db = session.query(Achievement).count()
        logger.info(f"Total achievements in database: {total_in_db}")

        return {
            'success': True,
            'added': added_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total': total_in_db
        }

    except Exception as e:
        logger.error(f"Error seeding achievements: {e}")
        session.rollback()
        raise

    finally:
        session.close()


def main():
    """Main entry point for command-line execution"""
    # Get database URL from command line argument if provided
    database_url = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        result = seed_achievements(database_url)
        if result['success']:
            logger.info("✅ Achievement seeding completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Achievement seeding failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
