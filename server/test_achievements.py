"""
Test Achievement System

This script tests the achievement checking and unlocking system.
"""

import logging
from app import app
from models import Player
from achievement_service import get_achievement_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("\n" + "="*60)
    logger.info("Testing Achievement System")
    logger.info("="*60 + "\n")

    # Initialize achievement service
    achievement_service = get_achievement_service(app)

    logger.info("[1] Checking achievements for all players...")
    stats = achievement_service.check_all_players()

    logger.info(f"\nResults:")
    logger.info(f"  Players Checked: {stats['players_checked']}")
    logger.info(f"  Achievements Unlocked: {stats['achievements_unlocked']}")

    # Get detailed progress for main player
    logger.info("\n[2] Getting detailed progress for main player...")
    wallet = "AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG"

    progress = achievement_service.get_player_progress(wallet)

    if 'error' not in progress:
        logger.info(f"\nMain Player Achievement Progress:")
        logger.info(f"  Total Achievements: {progress['total_achievements']}")
        logger.info(f"  Unlocked: {progress['unlocked_count']}")
        logger.info(f"  Total AP from Achievements: {progress['total_ap_from_achievements']}")

        # Show unlocked achievements
        unlocked = [a for a in progress['achievements'] if a['unlocked']]
        logger.info(f"\n  Unlocked Achievements ({len(unlocked)}):")
        for ach in unlocked:
            logger.info(f"    • {ach['name']} ({ach['tier']}) - +{ach['ap_reward']} AP")

        # Show some in-progress achievements
        in_progress = [a for a in progress['achievements']
                      if not a['unlocked'] and 'progress' in a and a['progress'].get('percentage', 0) > 0]
        if in_progress:
            logger.info(f"\n  In Progress ({len(in_progress)}):")
            for ach in in_progress[:5]:  # Show first 5
                prog = ach['progress']
                logger.info(f"    • {ach['name']} - {prog.get('percentage', 0)}% "
                          f"({prog.get('current', 0)}/{prog.get('required', 0)})")

    # Display player stats
    with app.app_context():
        player = Player.query.filter_by(wallet_address=wallet).first()
        if player:
            logger.info(f"\nUpdated Player Stats:")
            logger.info(f"  Total AP: {player.total_ap}")
            logger.info(f"  Available AP: {player.available_ap}")
            logger.info(f"  Total Mined ADVC: {player.total_mined_advc}")

    logger.info("\n" + "="*60)
    logger.info("Achievement Testing Complete!")
    logger.info("="*60 + "\n")


if __name__ == '__main__':
    main()
