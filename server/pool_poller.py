"""Pool Polling Service for monitoring mining pools and detecting player rewards."""

import asyncio
import signal
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import aiohttp
import structlog
import socketio

from sqlalchemy.orm import Session
from sqlalchemy import select

from config import settings
from server.models import Player, PoolSnapshot, MiningEvent
from server.database import SessionLocal


# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PoolPollerMetrics:
    """Track polling metrics for monitoring and debugging."""

    def __init__(self):
        self.polls_total = 0
        self.polls_successful = 0
        self.polls_failed = 0
        self.pool_stats = {}  # Per-pool statistics
        self.rewards_detected = 0
        self.start_time = datetime.utcnow()

    def record_poll(self, pool_name: str, success: bool, response_time: float):
        """Record a pool polling attempt."""
        if pool_name not in self.pool_stats:
            self.pool_stats[pool_name] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "total_response_time": 0.0,
            }

        stats = self.pool_stats[pool_name]
        stats["requests"] += 1
        stats["total_response_time"] += response_time

        if success:
            stats["successes"] += 1
            self.polls_successful += 1
        else:
            stats["failures"] += 1
            self.polls_failed += 1

        self.polls_total += 1

    def record_reward(self):
        """Record a detected reward."""
        self.rewards_detected += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of metrics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        summary = {
            "uptime_seconds": uptime,
            "polls_total": self.polls_total,
            "polls_successful": self.polls_successful,
            "polls_failed": self.polls_failed,
            "rewards_detected": self.rewards_detected,
            "pools": {},
        }

        for pool_name, stats in self.pool_stats.items():
            avg_response_time = (
                stats["total_response_time"] / stats["requests"] if stats["requests"] > 0 else 0
            )
            summary["pools"][pool_name] = {
                "requests": stats["requests"],
                "successes": stats["successes"],
                "failures": stats["failures"],
                "success_rate": stats["successes"] / stats["requests"] if stats["requests"] > 0 else 0,
                "avg_response_time_ms": avg_response_time * 1000,
            }

        return summary


class PoolPoller:
    """Main pool polling service that monitors mining pools for player rewards."""

    def __init__(self, db_session_factory=None, socketio_client=None):
        """
        Initialize the PoolPoller.

        Args:
            db_session_factory: SQLAlchemy session factory (defaults to SessionLocal)
            socketio_client: SocketIO client for real-time notifications (optional)
        """
        self.db_session_factory = db_session_factory or SessionLocal
        self.sio = socketio_client
        self.metrics = PoolPollerMetrics()
        self.running = False
        self.shutdown_event = asyncio.Event()

        # Pool configurations
        self.pool_configs = self._build_pool_configs()

        logger.info(
            "pool_poller_initialized",
            poll_interval=settings.poll_interval_seconds,
            pools_enabled=len(self.pool_configs),
            pool_names=[p["name"] for p in self.pool_configs],
        )

    def _build_pool_configs(self) -> List[Dict[str, Any]]:
        """Build list of enabled pool configurations."""
        configs = []

        if settings.cpu_pool_enabled:
            configs.append({
                "name": "cpu-pool",
                "url_template": settings.cpu_pool_url + "?addr={wallet}",
                "parser": self.parse_cpu_pool,
            })

        if settings.rplant_enabled:
            configs.append({
                "name": "rplant",
                "url_template": settings.rplant_url + "/{wallet}",
                "parser": self.parse_rplant,
            })

        if settings.zpool_enabled:
            configs.append({
                "name": "zpool",
                "url_template": settings.zpool_url + "?address={wallet}",
                "parser": self.parse_zpool,
            })

        return configs

    # ========================================================================
    # Pool Parser Functions
    # ========================================================================

    def parse_cpu_pool(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Parse cpu-pool.com API response.

        Expected response: {totalHash, totalShares, immature, balance, paid}

        Returns:
            Dict with 'paid' field (cumulative payouts in ADVC)
        """
        try:
            return {
                "paid": float(data.get("paid", 0.0)),
                "total_hash": float(data.get("totalHash", 0.0)),
                "total_shares": float(data.get("totalShares", 0.0)),
                "immature": float(data.get("immature", 0.0)),
                "balance": float(data.get("balance", 0.0)),
            }
        except (ValueError, TypeError) as e:
            logger.error("cpu_pool_parse_error", error=str(e), data=data)
            return {"paid": 0.0}

    def parse_rplant(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Parse rplant.xyz API response.

        Expected response format (to be confirmed):
        {
            "stats": {
                "paid": <amount>,
                "balance": <amount>,
                ...
            }
        }

        Note: API format needs discovery. This is a best-guess implementation.

        Returns:
            Dict with 'paid' field (cumulative payouts in ADVC)
        """
        try:
            # Try multiple possible response structures
            if "stats" in data:
                stats = data["stats"]
                paid = float(stats.get("paid", 0.0))
            elif "paid" in data:
                paid = float(data.get("paid", 0.0))
            elif "totalPaid" in data:
                paid = float(data.get("totalPaid", 0.0))
            else:
                logger.warning("rplant_unknown_format", data=data)
                paid = 0.0

            return {
                "paid": paid,
                "balance": float(data.get("balance", 0.0)),
            }
        except (ValueError, TypeError) as e:
            logger.error("rplant_parse_error", error=str(e), data=data)
            return {"paid": 0.0}

    def parse_zpool(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Parse zpool.ca API response.

        Expected response: {currency, unsold, balance, unpaid, paid, total}
        Note: zpool pays in BTC, need conversion to ADVC equivalent

        Returns:
            Dict with 'paid' field (cumulative payouts in ADVC equivalent)
        """
        try:
            paid_btc = float(data.get("paid", 0.0))
            # Convert BTC to ADVC using configured rate
            paid_advc = paid_btc * settings.btc_to_advc_rate

            return {
                "paid": paid_advc,
                "balance": float(data.get("balance", 0.0)) * settings.btc_to_advc_rate,
                "unpaid": float(data.get("unpaid", 0.0)) * settings.btc_to_advc_rate,
                "unsold": float(data.get("unsold", 0.0)) * settings.btc_to_advc_rate,
            }
        except (ValueError, TypeError) as e:
            logger.error("zpool_parse_error", error=str(e), data=data)
            return {"paid": 0.0}

    # ========================================================================
    # Core Polling Methods
    # ========================================================================

    async def poll_player(self, session: aiohttp.ClientSession, player: Player):
        """
        Poll all configured pools for a single player.

        Args:
            session: aiohttp ClientSession for making HTTP requests
            player: Player object to poll
        """
        tasks = []
        for pool_config in self.pool_configs:
            task = self._poll_single_pool(session, player, pool_config)
            tasks.append(task)

        # Run all pool polls concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _poll_single_pool(
        self,
        session: aiohttp.ClientSession,
        player: Player,
        pool_config: Dict[str, Any]
    ):
        """Poll a single pool for a player."""
        pool_name = pool_config["name"]
        url = pool_config["url_template"].format(wallet=player.wallet_address)
        parser = pool_config["parser"]

        start_time = asyncio.get_event_loop().time()

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=settings.pool_request_timeout)) as response:
                response_time = asyncio.get_event_loop().time() - start_time

                if response.status == 200:
                    data = await response.json()
                    self.metrics.record_poll(pool_name, True, response_time)

                    # Parse pool-specific data
                    parsed_data = parser(data)

                    # Process the data
                    await self.process_pool_data(player, pool_name, parsed_data, raw_data=data)

                    logger.debug(
                        "pool_poll_success",
                        player_id=player.id,
                        username=player.username,
                        pool=pool_name,
                        paid=parsed_data.get("paid", 0.0),
                        response_time_ms=response_time * 1000,
                    )
                else:
                    response_time = asyncio.get_event_loop().time() - start_time
                    self.metrics.record_poll(pool_name, False, response_time)
                    logger.warning(
                        "pool_poll_http_error",
                        player_id=player.id,
                        pool=pool_name,
                        status=response.status,
                        response_time_ms=response_time * 1000,
                    )

        except asyncio.TimeoutError:
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_poll(pool_name, False, response_time)
            logger.warning(
                "pool_poll_timeout",
                player_id=player.id,
                pool=pool_name,
                timeout=settings.pool_request_timeout,
            )
        except aiohttp.ClientError as e:
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_poll(pool_name, False, response_time)
            logger.error(
                "pool_poll_client_error",
                player_id=player.id,
                pool=pool_name,
                error=str(e),
            )
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_poll(pool_name, False, response_time)
            logger.error(
                "pool_poll_unexpected_error",
                player_id=player.id,
                pool=pool_name,
                error=str(e),
                traceback=traceback.format_exc(),
            )

    async def process_pool_data(
        self,
        player: Player,
        pool_name: str,
        data: Dict[str, float],
        raw_data: Optional[Dict] = None
    ):
        """
        Process pool data and detect/reward mining events.

        Args:
            player: Player object
            pool_name: Name of the pool
            data: Parsed pool data with 'paid' field
            raw_data: Raw API response (optional, for debugging)
        """
        try:
            current_paid = data.get("paid", 0.0)

            # Create a new database session for this transaction
            db = self.db_session_factory()
            try:
                # Refresh player object in this session
                db.add(player)
                db.refresh(player)

                # Query last snapshot for this player+pool
                last_snapshot = (
                    db.query(PoolSnapshot)
                    .filter(
                        PoolSnapshot.player_id == player.id,
                        PoolSnapshot.pool_name == pool_name,
                    )
                    .order_by(PoolSnapshot.snapshot_time.desc())
                    .first()
                )

                last_paid = last_snapshot.paid if last_snapshot else 0.0
                delta = current_paid - last_paid

                # Check if there's a significant payout
                if delta > settings.min_payout_delta:
                    # Calculate AP reward
                    ap_awarded = delta * settings.ap_per_advc

                    # Create mining event
                    mining_event = MiningEvent(
                        player_id=player.id,
                        pool_name=pool_name,
                        advc_amount=delta,
                        ap_awarded=ap_awarded,
                        previous_paid=last_paid,
                        current_paid=current_paid,
                        processed=True,
                        notified=False,
                    )
                    db.add(mining_event)

                    # Update player totals
                    player.total_ap += ap_awarded
                    player.total_advc_mined += delta
                    player.last_mining_event = datetime.utcnow()

                    # Commit the changes
                    db.commit()

                    # Record metric
                    self.metrics.record_reward()

                    # Emit WebSocket notification
                    await self._notify_player(player, mining_event)

                    logger.info(
                        "mining_reward_detected",
                        player_id=player.id,
                        username=player.username,
                        pool=pool_name,
                        advc_amount=delta,
                        ap_awarded=ap_awarded,
                        total_ap=player.total_ap,
                        total_advc_mined=player.total_advc_mined,
                    )

                    # Update notification status
                    mining_event.notified = True
                    db.commit()

                # Save new snapshot regardless of whether reward was detected
                new_snapshot = PoolSnapshot(
                    player_id=player.id,
                    pool_name=pool_name,
                    paid=current_paid,
                    total_hash=data.get("total_hash", 0.0),
                    total_shares=data.get("total_shares", 0.0),
                    immature=data.get("immature", 0.0),
                    balance=data.get("balance", 0.0),
                    raw_response=json.dumps(raw_data) if raw_data else None,
                )
                db.add(new_snapshot)
                db.commit()

            finally:
                db.close()

        except Exception as e:
            logger.error(
                "process_pool_data_error",
                player_id=player.id,
                pool=pool_name,
                error=str(e),
                traceback=traceback.format_exc(),
            )

    async def _notify_player(self, player: Player, mining_event: MiningEvent):
        """
        Send real-time notification to player via WebSocket.

        Args:
            player: Player object
            mining_event: MiningEvent object
        """
        if not self.sio:
            logger.debug("socketio_not_configured", player_id=player.id)
            return

        try:
            # Emit event to player's room (assuming player is in a room with their user ID)
            await self.sio.emit(
                "mining_reward",
                {
                    "player_id": player.id,
                    "username": player.username,
                    "pool": mining_event.pool_name,
                    "advc_amount": mining_event.advc_amount,
                    "ap_awarded": mining_event.ap_awarded,
                    "total_ap": player.total_ap,
                    "total_advc_mined": player.total_advc_mined,
                    "timestamp": mining_event.event_time.isoformat(),
                },
                room=f"player_{player.id}",
            )

            logger.debug(
                "player_notified",
                player_id=player.id,
                event_id=mining_event.id,
            )

        except Exception as e:
            logger.error(
                "notification_error",
                player_id=player.id,
                error=str(e),
            )

    async def poll_all_players(self):
        """Poll all verified players across all configured pools."""
        try:
            # Get all verified players
            db = self.db_session_factory()
            try:
                players = db.query(Player).filter(
                    Player.verified == True,
                    Player.active == True,
                ).all()

                # Detach players from session to use in async context
                player_list = [(p.id, p.username, p.wallet_address) for p in players]

            finally:
                db.close()

            if not player_list:
                logger.info("no_players_to_poll")
                return

            logger.info(
                "polling_cycle_start",
                player_count=len(player_list),
                pools=len(self.pool_configs),
            )

            # Create aiohttp session
            async with aiohttp.ClientSession() as session:
                # Create tasks for each player
                tasks = []
                for player_id, username, wallet in player_list:
                    # Recreate player object for async context
                    db = self.db_session_factory()
                    try:
                        player = db.query(Player).filter(Player.id == player_id).first()
                        if player:
                            task = self.poll_player(session, player)
                            tasks.append(task)
                    finally:
                        db.close()

                # Run all player polls concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Count failures
                failures = sum(1 for r in results if isinstance(r, Exception))
                if failures > 0:
                    logger.warning(
                        "polling_cycle_partial_failures",
                        total_players=len(player_list),
                        failures=failures,
                    )

            logger.info(
                "polling_cycle_complete",
                player_count=len(player_list),
                failures=failures,
                metrics=self.metrics.get_summary(),
            )

        except Exception as e:
            logger.error(
                "poll_all_players_error",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    async def run_forever(self):
        """Main polling loop that runs indefinitely."""
        self.running = True
        logger.info("pool_poller_started", interval=settings.poll_interval_seconds)

        try:
            while self.running:
                # Run polling cycle
                await self.poll_all_players()

                # Wait for next cycle or shutdown signal
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(),
                        timeout=settings.poll_interval_seconds,
                    )
                    # If we reach here, shutdown was signaled
                    break
                except asyncio.TimeoutError:
                    # Timeout is expected, continue to next cycle
                    pass

        except Exception as e:
            logger.error(
                "run_forever_error",
                error=str(e),
                traceback=traceback.format_exc(),
            )
        finally:
            logger.info("pool_poller_stopped")

    def stop(self):
        """Signal the poller to stop gracefully."""
        logger.info("shutdown_signal_received")
        self.running = False
        self.shutdown_event.set()


# ========================================================================
# Main Entry Point
# ========================================================================

async def main():
    """Main entry point for running the pool poller as a standalone service."""
    # Initialize SocketIO client (optional)
    sio = None
    if settings.socketio_url:
        try:
            sio = socketio.AsyncClient(logger=False, engineio_logger=False)
            await sio.connect(settings.socketio_url)
            logger.info("socketio_connected", url=settings.socketio_url)
        except Exception as e:
            logger.warning("socketio_connection_failed", error=str(e))
            sio = None

    # Create poller
    poller = PoolPoller(socketio_client=sio)

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("signal_received", signal=sig)
        poller.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run poller
    try:
        await poller.run_forever()
    finally:
        # Cleanup
        if sio and sio.connected:
            await sio.disconnect()
        logger.info("cleanup_complete")


if __name__ == "__main__":
    asyncio.run(main())
