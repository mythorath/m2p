"""
Create Test Data for M2P System

This script creates realistic test data including players, mining events,
and achievements to demonstrate the full system functionality.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app import app, db
from models import Player, MiningEvent
from achievement_service import get_achievement_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_player(wallet_address: str, display_name: str, verified=False) -> str:
    """Create or get a player."""
    with app.app_context():
        player = Player.query.filter_by(wallet_address=wallet_address).first()

        if not player:
            player = Player(
                wallet_address=wallet_address,
                display_name=display_name,
                verified=verified,
                total_ap=0,
                spent_ap=0,
                total_mined_advc=Decimal('0'),
                total_advc=Decimal('0'),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(player)
            db.session.commit()
            logger.info(f"Created player: {display_name} ({wallet_address})")
        else:
            logger.info(f"Player already exists: {display_name}")

        return wallet_address


def create_mining_events(wallet_address: str, num_events: int, pools: list):
    """Create mining events for a player."""
    with app.app_context():
        player_obj = Player.query.filter_by(wallet_address=wallet_address).first()

        if not player_obj:
            logger.error(f"Player not found: {wallet_address}")
            return 0

        events_created = 0
        total_advc = Decimal('0')
        total_ap = 0

        for i in range(num_events):
            # Random mining amount between 0.01 and 5.0 ADVC
            amount = Decimal(str(round(random.uniform(0.01, 5.0), 8)))

            # Calculate AP (1 ADVC = 10 AP)
            ap = int(amount * 10)

            # Random pool
            pool = random.choice(pools)

            # Random time in the past 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

            # Create event
            event = MiningEvent(
                wallet_address=wallet_address,
                amount_advc=amount,
                ap_awarded=ap,
                pool=pool,
                timestamp=timestamp,
                tx_hash=f"tx_{wallet_address}_{i}_{int(timestamp.timestamp())}"
            )

            db.session.add(event)
            events_created += 1
            total_advc += amount
            total_ap += ap

        # Update player totals
        player_obj.total_mined_advc += total_advc
        player_obj.total_advc += total_advc
        player_obj.total_ap += total_ap

        db.session.commit()

        logger.info(f"Created {events_created} mining events for {player_obj.display_name}")
        logger.info(f"  Total ADVC: {total_advc}")
        logger.info(f"  Total AP: {total_ap}")

        return events_created


def main():
    """Create comprehensive test data."""
    logger.info("\n" + "="*60)
    logger.info("Creating M2P Test Data")
    logger.info("="*60 + "\n")

    # Ensure fresh database schema
    logger.info("[0] Ensuring fresh database schema...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        logger.info("Database schema refreshed")

    pools = ["WellcoDigital", "CPU-Pool", "MiningPoolHub"]

    # Create test players
    logger.info("\n[1] Creating test players...")

    # Main test player (your wallet)
    main_player = create_player(
        wallet_address="AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG",
        display_name="TestMiner_Main",
        verified=True
    )

    # Additional test players for leaderboard
    test_players = [
        create_player(f"A{chr(65+i)}{'x'*31}", f"TestMiner_{i+1}", random.choice([True, False]))
        for i in range(10)
    ]

    # Create mining events
    logger.info("\n[2] Creating mining events...")

    # Main player gets significant mining activity
    create_mining_events(main_player, 50, pools)

    # Other players get varying amounts
    for i, player in enumerate(test_players):
        num_events = random.randint(5, 30)
        create_mining_events(player, num_events, pools)

    # Check achievements
    logger.info("\n[3] Checking achievements...")
    achievement_service = get_achievement_service(app)

    with app.app_context():
        # Check all players
        all_players = Player.query.all()
        total_unlocked = 0

        for player in all_players:
            unlocked = achievement_service.check_player_achievements(player.wallet_address)
            if unlocked:
                logger.info(f"  {player.display_name} unlocked {len(unlocked)} achievements!")
                total_unlocked += len(unlocked)

        logger.info(f"\n  Total achievements unlocked: {total_unlocked}")

    # Display summary
    logger.info("\n" + "="*60)
    logger.info("Test Data Summary")
    logger.info("="*60)

    with app.app_context():
        total_players = Player.query.count()
        total_events = MiningEvent.query.count()
        total_advc = db.session.query(db.func.sum(Player.total_mined_advc)).scalar() or Decimal('0')
        total_ap = db.session.query(db.func.sum(Player.total_ap)).scalar() or 0

        logger.info(f"Players Created: {total_players}")
        logger.info(f"Mining Events: {total_events}")
        logger.info(f"Total ADVC Mined: {total_advc}")
        logger.info(f"Total AP Awarded: {total_ap}")

        # Show main player stats
        main = Player.query.filter_by(wallet_address="AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG").first()
        if main:
            logger.info(f"\nMain Test Player Stats:")
            logger.info(f"  Wallet: {main.wallet_address}")
            logger.info(f"  Display Name: {main.display_name}")
            logger.info(f"  Total Mined ADVC: {main.total_mined_advc}")
            logger.info(f"  Total AP: {main.total_ap}")
            logger.info(f"  Verified: {main.verified}")
            logger.info(f"  Mining Events: {main.mining_events.count()}")

            # Show unlocked achievements
            from models import PlayerAchievement
            achievements = PlayerAchievement.query.filter_by(
                wallet_address=main.wallet_address
            ).all()

            logger.info(f"  Unlocked Achievements: {len(achievements)}")
            if achievements:
                for pa in achievements[:5]:  # Show first 5
                    logger.info(f"    • {pa.achievement.name} ({pa.achievement.tier}) - +{pa.achievement.ap_reward} AP")
                if len(achievements) > 5:
                    logger.info(f"    ... and {len(achievements) - 5} more")

    logger.info("\n" + "="*60)
    logger.info("Test Data Creation Complete!")
    logger.info("="*60 + "\n")


if __name__ == '__main__':
    main()
