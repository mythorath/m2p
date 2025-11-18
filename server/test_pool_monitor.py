"""
Test Pool Monitor with Real Wallet

This script tests the pool monitoring service with a real wallet address.
"""

import asyncio
import logging
from app import app, db
from models import Player, MiningEvent
from pool_monitor import create_monitoring_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_wallet_monitoring(wallet_address: str):
    """Test monitoring for a specific wallet."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Pool Monitoring for Wallet: {wallet_address}")
    logger.info(f"{'='*60}\n")

    # Create monitoring service
    service = create_monitoring_service(app)

    # Check the wallet
    logger.info("Checking all pools for mining activity...")
    new_events, total_amount = await service.check_wallet(wallet_address)

    logger.info(f"\n{'='*60}")
    logger.info(f"Results:")
    logger.info(f"  New Events Found: {new_events}")
    logger.info(f"  Total Amount: {total_amount} ADVC")
    logger.info(f"{'='*60}\n")

    # Display player info
    with app.app_context():
        player = Player.query.filter_by(wallet_address=wallet_address).first()
        if player:
            logger.info("Player Profile:")
            logger.info(f"  Display Name: {player.display_name}")
            logger.info(f"  Total Mined ADVC: {player.total_mined_advc}")
            logger.info(f"  Total AP: {player.total_ap}")
            logger.info(f"  Verified: {player.verified}")

            # Display mining events
            events = MiningEvent.query.filter_by(
                wallet_address=wallet_address
            ).order_by(MiningEvent.timestamp.desc()).limit(10).all()

            if events:
                logger.info(f"\n  Recent Mining Events ({len(events)}):")
                for event in events:
                    logger.info(f"    • {event.amount_advc} ADVC from {event.pool} "
                              f"(+{event.ap_awarded} AP) at {event.timestamp}")
            else:
                logger.info("\n  No mining events found yet.")
        else:
            logger.info("Player not found in database.")


async def test_individual_pools(wallet_address: str):
    """Test each pool individually."""
    from pool_monitor import WellcoDigitalMonitor, CPUPoolMonitor

    logger.info(f"\n{'='*60}")
    logger.info("Testing Individual Pool Monitors")
    logger.info(f"{'='*60}\n")

    # Test WellcoDigital
    logger.info("1. Testing WellcoDigital Monitor...")
    async with WellcoDigitalMonitor() as monitor:
        events = await monitor.get_mining_data(wallet_address)
        logger.info(f"   Found {len(events)} events")
        for event in events:
            logger.info(f"     • {event}")

    # Test CPU-Pool
    logger.info("\n2. Testing CPU-Pool Monitor...")
    async with CPUPoolMonitor() as monitor:
        events = await monitor.get_mining_data(wallet_address)
        logger.info(f"   Found {len(events)} events")
        for event in events:
            logger.info(f"     • {event}")


def main():
    """Main test function."""
    # Test wallet address
    test_wallet = "AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG"

    logger.info("\n" + "="*60)
    logger.info("M2P Pool Monitor Test Suite")
    logger.info("="*60)

    # Run tests
    loop = asyncio.get_event_loop()

    # Test individual pools first
    logger.info("\n[Phase 1] Testing individual pool monitors...")
    loop.run_until_complete(test_individual_pools(test_wallet))

    # Test full monitoring service
    logger.info("\n[Phase 2] Testing full monitoring service...")
    loop.run_until_complete(test_wallet_monitoring(test_wallet))

    logger.info("\n" + "="*60)
    logger.info("Test Complete!")
    logger.info("="*60 + "\n")


if __name__ == '__main__':
    main()
