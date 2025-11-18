"""
Pool Monitoring Service for M2P (Mine to Play)

This service monitors mining pools for player rewards and updates the database accordingly.
It supports multiple pools and can handle both API-based and web-scraping approaches.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re
import json

from models import db, Player, MiningEvent
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class PoolMonitor:
    """Base class for pool monitoring."""

    def __init__(self, pool_name: str, pool_url: str):
        self.pool_name = pool_name
        self.pool_url = pool_url
        self.session = None

    async def __aenter__(self):
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()

    async def fetch_url(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch URL content with error handling.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            Response text or None if failed
        """
        try:
            async with self.session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def get_mining_data(self, wallet_address: str) -> List[Dict]:
        """
        Get mining data for a wallet address.

        Must be implemented by subclasses.

        Returns:
            List of mining events as dictionaries
        """
        raise NotImplementedError("Subclasses must implement get_mining_data")


class WellcoDigitalMonitor(PoolMonitor):
    """Monitor for WellcoDigital pool."""

    def __init__(self):
        super().__init__("WellcoDigital", "https://wellcodigital.com")

    async def get_mining_data(self, wallet_address: str) -> List[Dict]:
        """
        Scrape mining data from WellcoDigital pool.

        Since they don't have a public API, we'll scrape the web interface.
        """
        events = []

        # Try to fetch the dashboard page
        dashboard_url = f"{self.pool_url}/?#adventurecoin-solo/dashboard?address={wallet_address}"

        html = await self.fetch_url(dashboard_url)
        if not html:
            logger.warning(f"Could not fetch WellcoDigital data for {wallet_address}")
            return events

        soup = BeautifulSoup(html, 'html.parser')

        # Try to find payment data
        # Note: This will need to be adjusted based on actual page structure
        # For now, we'll create a simulated event if we can confirm the wallet exists

        # Check if wallet address appears on the page
        if wallet_address in html:
            logger.info(f"Found wallet {wallet_address} on WellcoDigital")
            # Since we can't get detailed payment history without JavaScript execution,
            # we'll mark this for manual review or future enhancement

        return events


class CPUPoolMonitor(PoolMonitor):
    """Monitor for CPU-Pool.com."""

    def __init__(self):
        super().__init__("CPU-Pool", "http://cpu-pool.com")

    async def get_mining_data(self, wallet_address: str) -> List[Dict]:
        """
        Fetch mining data from CPU-Pool.

        Note: Pool may be experiencing issues (503 errors).
        """
        events = []

        # Try API endpoints
        api_endpoints = [
            f"{self.pool_url}/api/worker/{wallet_address}",
            f"{self.pool_url}/api/stats/{wallet_address}",
            f"{self.pool_url}/workers/{wallet_address}"
        ]

        for endpoint in api_endpoints:
            html = await self.fetch_url(endpoint)
            if html:
                # Try to parse as JSON first
                try:
                    data = json.loads(html)
                    events.extend(self._parse_api_data(data, wallet_address))
                    break
                except json.JSONDecodeError:
                    # Try HTML parsing
                    soup = BeautifulSoup(html, 'html.parser')
                    events.extend(self._parse_html_data(soup, wallet_address))
                    break

        return events

    def _parse_api_data(self, data: Dict, wallet_address: str) -> List[Dict]:
        """Parse API response data."""
        events = []

        # Handle different API response formats
        if isinstance(data, dict):
            if 'payments' in data:
                for payment in data['payments']:
                    events.append({
                        'wallet_address': wallet_address,
                        'pool_name': self.pool_name,
                        'amount': Decimal(str(payment.get('amount', 0))),
                        'timestamp': datetime.fromtimestamp(payment.get('time', 0)),
                        'tx_hash': payment.get('tx', '')
                    })

        return events

    def _parse_html_data(self, soup: BeautifulSoup, wallet_address: str) -> List[Dict]:
        """Parse HTML page data."""
        events = []

        # Look for payment tables or lists
        # This is a generic parser that will need adjustment

        return events


class PoolMonitoringService:
    """
    Main service for monitoring all mining pools.
    """

    def __init__(self, app):
        self.app = app
        self.monitors = {}
        self.running = False
        self.check_interval = 300  # Check every 5 minutes

    def register_monitor(self, monitor: PoolMonitor):
        """Register a pool monitor."""
        self.monitors[monitor.pool_name] = monitor

    async def check_wallet(self, wallet_address: str) -> Tuple[int, Decimal]:
        """
        Check a wallet across all pools and update database.

        Returns:
            Tuple of (new_events_count, total_amount)
        """
        new_events = 0
        total_amount = Decimal('0')

        for pool_name, monitor in self.monitors.items():
            async with monitor:
                try:
                    events = await monitor.get_mining_data(wallet_address)

                    for event_data in events:
                        # Check if event already exists
                        existing = await self._check_existing_event(
                            wallet_address,
                            event_data.get('tx_hash'),
                            event_data.get('timestamp')
                        )

                        if not existing:
                            await self._create_mining_event(event_data)
                            new_events += 1
                            total_amount += event_data.get('amount', Decimal('0'))

                except Exception as e:
                    logger.error(f"Error checking {pool_name} for {wallet_address}: {e}")

        return new_events, total_amount

    async def _check_existing_event(self, wallet: str, tx_hash: str,
                                    timestamp: datetime) -> bool:
        """Check if mining event already exists in database."""
        with self.app.app_context():
            if tx_hash:
                existing = MiningEvent.query.filter_by(
                    wallet_address=wallet,
                    tx_hash=tx_hash
                ).first()
            else:
                # If no tx_hash, check by timestamp and amount
                time_window = timedelta(minutes=5)
                existing = MiningEvent.query.filter(
                    MiningEvent.wallet_address == wallet,
                    MiningEvent.timestamp >= timestamp - time_window,
                    MiningEvent.timestamp <= timestamp + time_window
                ).first()

            return existing is not None

    async def _create_mining_event(self, event_data: Dict):
        """Create a new mining event in the database."""
        with self.app.app_context():
            try:
                # Get or create player
                player = Player.query.filter_by(
                    wallet_address=event_data['wallet_address']
                ).first()

                if not player:
                    player = Player(
                        wallet_address=event_data['wallet_address'],
                        display_name=f"Miner_{event_data['wallet_address'][:8]}"
                    )
                    db.session.add(player)

                # Calculate AP from ADVC amount
                # 1 ADVC = 10 AP for now (can be adjusted)
                ap_awarded = int(event_data['amount'] * 10)

                # Create mining event
                mining_event = MiningEvent(
                    wallet_address=event_data['wallet_address'],
                    pool=event_data.get('pool_name', 'Unknown'),
                    amount_advc=event_data['amount'],
                    ap_awarded=ap_awarded,
                    timestamp=event_data.get('timestamp', datetime.utcnow()),
                    tx_hash=event_data.get('tx_hash', '')
                )

                # Update player totals
                player.total_advc += event_data['amount']
                player.total_mined_advc += event_data['amount']
                player.total_ap += ap_awarded
                player.updated_at = datetime.utcnow()

                db.session.add(mining_event)
                db.session.commit()

                logger.info(f"Created mining event: {event_data['amount']} ADVC "
                          f"({ap_awarded} AP) for {event_data['wallet_address']}")

            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error creating mining event: {e}")
                raise

    async def monitor_loop(self):
        """Main monitoring loop."""
        logger.info("Starting pool monitoring service...")

        self.running = True

        while self.running:
            try:
                with self.app.app_context():
                    # Get all players
                    players = Player.query.all()

                    for player in players:
                        try:
                            new_events, amount = await self.check_wallet(
                                player.wallet_address
                            )

                            if new_events > 0:
                                logger.info(f"Found {new_events} new events for "
                                          f"{player.wallet_address}: {amount} ADVC")
                        except Exception as e:
                            logger.error(f"Error checking wallet {player.wallet_address}: {e}")

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    def stop(self):
        """Stop the monitoring service."""
        logger.info("Stopping pool monitoring service...")
        self.running = False


# Initialize the service
def create_monitoring_service(app):
    """Create and configure the pool monitoring service."""
    service = PoolMonitoringService(app)

    # Register monitors
    service.register_monitor(WellcoDigitalMonitor())
    service.register_monitor(CPUPoolMonitor())

    return service
