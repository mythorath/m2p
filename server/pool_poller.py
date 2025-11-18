"""
Pool polling service for M2P (Mine to Play)
Monitors mining pools and awards rewards to players
Integrates with achievement system
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from server.models import Player, MiningEvent, DailyMiningStats
from server.achievements import AchievementManager

logger = logging.getLogger(__name__)


class PoolPoller:
    """Polls mining pools and processes rewards"""

    def __init__(self, db_session: Session, websocket_manager=None):
        """
        Initialize the pool poller.

        Args:
            db_session: SQLAlchemy database session
            websocket_manager: WebSocket manager for real-time notifications
        """
        self.db = db_session
        self.ws_manager = websocket_manager
        self.achievement_manager = AchievementManager(db_session)
        self.polling_interval = 60  # seconds
        self.is_running = False

    async def start(self):
        """Start the pool polling loop"""
        self.is_running = True
        logger.info("Pool poller started")

        while self.is_running:
            try:
                await self.poll_all_pools()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in pool polling loop: {e}", exc_info=True)
                await asyncio.sleep(self.polling_interval)

    def stop(self):
        """Stop the pool polling loop"""
        self.is_running = False
        logger.info("Pool poller stopped")

    async def poll_all_pools(self):
        """
        Poll all mining pools and process rewards.
        In a real implementation, this would call actual pool APIs.
        """
        logger.debug("Polling all pools...")

        # TODO: Implement actual pool API calls
        # For now, this is a placeholder that would:
        # 1. Query each pool's API for player rewards
        # 2. Process each reward
        # 3. Update player stats
        # 4. Check achievements

        # Example pools (in real implementation, these would come from config/database)
        pools = [
            {'id': 'pool_1', 'name': 'MainPool', 'api_url': 'https://pool1.example.com/api'},
            {'id': 'pool_2', 'name': 'BackupPool', 'api_url': 'https://pool2.example.com/api'},
        ]

        for pool in pools:
            try:
                await self.poll_pool(pool)
            except Exception as e:
                logger.error(f"Error polling pool {pool['name']}: {e}")

    async def poll_pool(self, pool: Dict):
        """
        Poll a specific mining pool.

        Args:
            pool: Dict with pool information (id, name, api_url)
        """
        # TODO: Implement actual API call to pool
        # This is a placeholder showing the structure

        # Example: Get rewards from pool API
        # rewards = await self._fetch_pool_rewards(pool['api_url'])

        # For demonstration, we'll process any pending rewards
        logger.debug(f"Polled pool: {pool['name']}")

    async def process_mining_reward(
        self,
        player_id: int,
        amount: float,
        pool_id: str,
        pool_name: str
    ) -> Dict:
        """
        Process a mining reward for a player.
        This is the main entry point for awarding mining rewards.

        Args:
            player_id: The player's database ID
            amount: Amount of ADVC mined
            pool_id: Pool identifier
            pool_name: Human-readable pool name

        Returns:
            Dict with reward info and any unlocked achievements
        """
        logger.info(f"Processing mining reward: Player {player_id}, Amount: {amount}, Pool: {pool_name}")

        # Get player from database
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            logger.error(f"Player not found: {player_id}")
            raise ValueError(f"Player {player_id} not found")

        # Create mining event
        mining_event = MiningEvent(
            player_id=player.id,
            amount_mined=amount,
            pool_id=pool_id,
            pool_name=pool_name,
            timestamp=datetime.utcnow()
        )
        self.db.add(mining_event)

        # Update player stats
        player.total_mined += amount
        player.total_mining_events += 1
        player.last_active = datetime.utcnow()

        # Update unique pools list
        if player.unique_pools_mined is None:
            player.unique_pools_mined = []

        if pool_id not in player.unique_pools_mined:
            player.unique_pools_mined = player.unique_pools_mined + [pool_id]

        # Update consecutive mining days
        self._update_consecutive_days(player)

        # Update daily stats
        self._update_daily_stats(player, amount, pool_id)

        # Commit player updates before checking achievements
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing mining reward: {e}")
            self.db.rollback()
            raise

        # Check for newly unlocked achievements
        newly_unlocked = self.achievement_manager.check_achievements(player)

        # Prepare response
        result = {
            'player_id': player.id,
            'username': player.username,
            'amount_mined': amount,
            'total_mined': player.total_mined,
            'total_ap': player.total_ap,
            'pool_name': pool_name,
            'newly_unlocked_achievements': newly_unlocked
        }

        # Send WebSocket notifications
        if self.ws_manager:
            await self._send_notifications(player, amount, newly_unlocked)

        logger.info(
            f"Mining reward processed: {player.username} mined {amount} ADVC, "
            f"Total: {player.total_mined}, AP: {player.total_ap}, "
            f"Achievements unlocked: {len(newly_unlocked)}"
        )

        return result

    def _update_consecutive_days(self, player: Player):
        """Update the player's consecutive mining days streak"""
        today = datetime.utcnow().date()

        if player.last_mining_date is None:
            # First mining event
            player.consecutive_mining_days = 1
            player.last_mining_date = datetime.utcnow()
        else:
            last_mining_date = player.last_mining_date.date()

            if last_mining_date == today:
                # Already mined today, no change to streak
                pass
            elif last_mining_date == today - timedelta(days=1):
                # Mined yesterday, increment streak
                player.consecutive_mining_days += 1
                player.last_mining_date = datetime.utcnow()
            elif last_mining_date < today - timedelta(days=1):
                # Streak broken, reset to 1
                player.consecutive_mining_days = 1
                player.last_mining_date = datetime.utcnow()

    def _update_daily_stats(self, player: Player, amount: float, pool_id: str):
        """Update or create daily mining statistics"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Find or create today's stats
        daily_stats = self.db.query(DailyMiningStats).filter(
            DailyMiningStats.player_id == player.id,
            DailyMiningStats.date == today
        ).first()

        if daily_stats:
            # Update existing stats
            daily_stats.total_mined += amount
            daily_stats.mining_events_count += 1

            # Add pool to unique pools if not already there
            if pool_id not in daily_stats.unique_pools:
                daily_stats.unique_pools = daily_stats.unique_pools + [pool_id]
        else:
            # Create new daily stats
            daily_stats = DailyMiningStats(
                player_id=player.id,
                date=today,
                total_mined=amount,
                mining_events_count=1,
                unique_pools=[pool_id]
            )
            self.db.add(daily_stats)

    async def _send_notifications(self, player: Player, amount: float, achievements: List[Dict]):
        """Send WebSocket notifications for mining reward and achievements"""
        if not self.ws_manager:
            return

        # Send mining reward notification
        await self.ws_manager.send_to_user(player.id, {
            'type': 'mining_reward',
            'amount': amount,
            'total_mined': player.total_mined,
            'total_ap': player.total_ap
        })

        # Send achievement unlock notifications
        for achievement in achievements:
            await self.ws_manager.send_to_user(player.id, {
                'type': 'achievement_unlocked',
                'achievement': achievement
            })

    def get_player_mining_stats(self, player_id: int) -> Optional[Dict]:
        """
        Get comprehensive mining statistics for a player.

        Args:
            player_id: The player's database ID

        Returns:
            Dict with mining statistics or None if player not found
        """
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None

        # Get recent mining events (last 10)
        recent_events = self.db.query(MiningEvent).filter(
            MiningEvent.player_id == player.id
        ).order_by(MiningEvent.timestamp.desc()).limit(10).all()

        # Get daily stats for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = self.db.query(DailyMiningStats).filter(
            DailyMiningStats.player_id == player.id,
            DailyMiningStats.date >= thirty_days_ago
        ).order_by(DailyMiningStats.date.desc()).all()

        return {
            'total_mined': player.total_mined,
            'total_mining_events': player.total_mining_events,
            'consecutive_days': player.consecutive_mining_days,
            'unique_pools_count': len(player.unique_pools_mined or []),
            'total_ap': player.total_ap,
            'last_mining_date': player.last_mining_date.isoformat() if player.last_mining_date else None,
            'recent_events': [
                {
                    'amount': event.amount_mined,
                    'pool_name': event.pool_name,
                    'timestamp': event.timestamp.isoformat()
                }
                for event in recent_events
            ],
            'daily_history': [
                {
                    'date': stats.date.isoformat(),
                    'total_mined': stats.total_mined,
                    'events_count': stats.mining_events_count
                }
                for stats in daily_stats
            ]
        }
