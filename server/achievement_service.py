"""
Achievement Service for M2P (Mine to Play)

This service handles achievement checking, unlocking, and AP rewards.
It evaluates player progress against achievement criteria and automatically
unlocks achievements when conditions are met.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import json

from models import db, Player, Achievement, PlayerAchievement, MiningEvent
from sqlalchemy import func

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievement unlocking and tracking."""

    def __init__(self, app=None, socketio=None):
        self.app = app
        self.socketio = socketio

    def check_player_achievements(self, wallet_address: str) -> List[Dict]:
        """
        Check all achievements for a player and unlock any that are newly earned.

        Args:
            wallet_address: Player's wallet address

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        with self.app.app_context():
            player = Player.query.filter_by(wallet_address=wallet_address).first()
            if not player:
                logger.warning(f"Player not found: {wallet_address}")
                return newly_unlocked

            # Get all achievements
            all_achievements = Achievement.query.all()

            # Get already unlocked achievement IDs
            unlocked_ids = set(
                pa.achievement_id for pa in
                PlayerAchievement.query.filter_by(wallet_address=wallet_address).all()
            )

            for achievement in all_achievements:
                # Skip if already unlocked
                if achievement.id in unlocked_ids:
                    continue

                # Check if criteria is met
                if self._check_criteria(player, achievement):
                    unlocked = self._unlock_achievement(player, achievement)
                    if unlocked:
                        newly_unlocked.append(unlocked)

        return newly_unlocked

    def _check_criteria(self, player: Player, achievement: Achievement) -> bool:
        """
        Check if player meets achievement criteria.

        Args:
            player: Player object
            achievement: Achievement object

        Returns:
            True if criteria is met, False otherwise
        """
        if not achievement.criteria:
            return False

        try:
            criteria = json.loads(achievement.criteria)
            criteria_type = criteria.get('type')

            # Registration achievement
            if criteria_type == 'registration':
                return True

            # Verification achievement
            elif criteria_type == 'verification':
                return player.verified

            # Mining amount achievements
            elif criteria_type == 'mine_amount':
                required = Decimal(str(criteria.get('amount', 0)))
                return player.total_mined_advc >= required

            # Total ADVC achievements
            elif criteria_type == 'total_advc':
                required = Decimal(str(criteria.get('amount', 0)))
                return player.total_mined_advc >= required

            # Mining event count achievements
            elif criteria_type == 'mining_events':
                count = player.mining_events.count()
                required = criteria.get('count', 0)
                return count >= required

            # AP achievements
            elif criteria_type == 'total_ap':
                required = criteria.get('amount', 0)
                return player.total_ap >= required

            # Spending achievements
            elif criteria_type == 'spend_ap':
                required = criteria.get('amount', 0)
                return player.spent_ap >= required

            # Time-based achievements
            elif criteria_type == 'active_days':
                required_days = criteria.get('days', 0)
                if player.created_at:
                    days_active = (datetime.utcnow() - player.created_at).days
                    return days_active >= required_days
                return False

            # Consecutive days achievement
            elif criteria_type == 'consecutive_days':
                required_days = criteria.get('days', 0)
                return self._check_consecutive_mining_days(player, required_days)

            # Leaderboard achievement
            elif criteria_type == 'leaderboard_rank':
                required_rank = criteria.get('rank', 1)
                current_rank = self._get_player_rank(player)
                return current_rank <= required_rank

            # Early adopter (join by specific date)
            elif criteria_type == 'join_before':
                deadline = datetime.fromisoformat(criteria.get('date'))
                return player.created_at <= deadline if player.created_at else False

            # Lucky strike (single large mining event)
            elif criteria_type == 'single_event_amount':
                required = Decimal(str(criteria.get('amount', 0)))
                max_event = db.session.query(func.max(MiningEvent.amount_advc)).filter(
                    MiningEvent.wallet_address == player.wallet_address
                ).scalar()
                return max_event and max_event >= required

            # Night owl (mine between specific hours)
            elif criteria_type == 'time_of_day':
                start_hour = criteria.get('start_hour', 0)
                end_hour = criteria.get('end_hour', 6)
                count = criteria.get('count', 10)

                night_events = MiningEvent.query.filter(
                    MiningEvent.wallet_address == player.wallet_address,
                    func.extract('hour', MiningEvent.timestamp) >= start_hour,
                    func.extract('hour', MiningEvent.timestamp) < end_hour
                ).count()

                return night_events >= count

            # Pool diversity
            elif criteria_type == 'pool_count':
                required_pools = criteria.get('count', 2)
                unique_pools = db.session.query(func.count(func.distinct(MiningEvent.pool))).filter(
                    MiningEvent.wallet_address == player.wallet_address
                ).scalar()
                return unique_pools >= required_pools

            else:
                logger.warning(f"Unknown criteria type: {criteria_type}")
                return False

        except json.JSONDecodeError:
            logger.error(f"Invalid criteria JSON for achievement {achievement.id}")
            return False
        except Exception as e:
            logger.error(f"Error checking criteria for achievement {achievement.id}: {e}")
            return False

    def _check_consecutive_mining_days(self, player: Player, required_days: int) -> bool:
        """
        Check if player has mined for consecutive days.

        Args:
            player: Player object
            required_days: Number of consecutive days required

        Returns:
            True if requirement is met
        """
        # Get all mining event dates
        events = MiningEvent.query.filter_by(
            wallet_address=player.wallet_address
        ).order_by(MiningEvent.timestamp.desc()).all()

        if not events:
            return False

        # Get unique dates
        dates = set(event.timestamp.date() for event in events)
        sorted_dates = sorted(dates, reverse=True)

        # Check for consecutive days
        consecutive = 1
        for i in range(len(sorted_dates) - 1):
            if (sorted_dates[i] - sorted_dates[i + 1]).days == 1:
                consecutive += 1
                if consecutive >= required_days:
                    return True
            else:
                consecutive = 1

        return consecutive >= required_days

    def _get_player_rank(self, player: Player) -> int:
        """
        Get player's current leaderboard rank by AP.

        Args:
            player: Player object

        Returns:
            Player's rank (1-indexed)
        """
        rank = db.session.query(func.count(Player.wallet_address)).filter(
            Player.total_ap > player.total_ap
        ).scalar()

        return rank + 1 if rank is not None else 1

    def _unlock_achievement(self, player: Player, achievement: Achievement) -> Optional[Dict]:
        """
        Unlock an achievement for a player and award AP.

        Args:
            player: Player object
            achievement: Achievement object

        Returns:
            Dictionary with achievement details if unlocked, None otherwise
        """
        try:
            # Create player achievement record
            player_achievement = PlayerAchievement(
                wallet_address=player.wallet_address,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow()
            )

            # Award AP
            player.total_ap += achievement.ap_reward

            db.session.add(player_achievement)
            db.session.commit()

            logger.info(f"Achievement unlocked: {achievement.name} for {player.wallet_address} "
                       f"(+{achievement.ap_reward} AP)")

            achievement_data = {
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'tier': achievement.tier,
                'ap_reward': achievement.ap_reward,
                'icon': achievement.icon,
                'unlocked_at': player_achievement.unlocked_at.isoformat()
            }

            # Send WebSocket notification if available
            if self.socketio:
                self.socketio.emit('achievement_unlocked', achievement_data,
                                  room=player.wallet_address)

            return achievement_data

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unlocking achievement {achievement.id} for {player.wallet_address}: {e}")
            return None

    def check_all_players(self) -> Dict[str, int]:
        """
        Check achievements for all players.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'players_checked': 0,
            'achievements_unlocked': 0
        }

        with self.app.app_context():
            players = Player.query.all()

            for player in players:
                newly_unlocked = self.check_player_achievements(player.wallet_address)
                stats['players_checked'] += 1
                stats['achievements_unlocked'] += len(newly_unlocked)

                if newly_unlocked:
                    logger.info(f"Player {player.wallet_address} unlocked {len(newly_unlocked)} achievements")

        return stats

    def get_player_progress(self, wallet_address: str) -> Dict:
        """
        Get detailed achievement progress for a player.

        Args:
            wallet_address: Player's wallet address

        Returns:
            Dictionary with achievement progress data
        """
        with self.app.app_context():
            player = Player.query.filter_by(wallet_address=wallet_address).first()
            if not player:
                return {'error': 'Player not found'}

            all_achievements = Achievement.query.all()
            unlocked = PlayerAchievement.query.filter_by(wallet_address=wallet_address).all()
            unlocked_dict = {pa.achievement_id: pa for pa in unlocked}

            progress = {
                'total_achievements': len(all_achievements),
                'unlocked_count': len(unlocked),
                'total_ap_from_achievements': sum(a.achievement.ap_reward for a in unlocked),
                'achievements': []
            }

            for achievement in all_achievements:
                ach_data = {
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'tier': achievement.tier,
                    'ap_reward': achievement.ap_reward,
                    'category': achievement.category,
                    'unlocked': achievement.id in unlocked_dict
                }

                if achievement.id in unlocked_dict:
                    ach_data['unlocked_at'] = unlocked_dict[achievement.id].unlocked_at.isoformat()
                else:
                    # Calculate progress towards unlocking
                    ach_data['progress'] = self._calculate_progress(player, achievement)

                progress['achievements'].append(ach_data)

            return progress

    def _calculate_progress(self, player: Player, achievement: Achievement) -> Dict:
        """
        Calculate player's progress towards an achievement.

        Args:
            player: Player object
            achievement: Achievement object

        Returns:
            Dictionary with progress information
        """
        if not achievement.criteria:
            return {'percentage': 0, 'current': 0, 'required': 0}

        try:
            criteria = json.loads(achievement.criteria)
            criteria_type = criteria.get('type')

            if criteria_type in ['mine_amount', 'total_advc']:
                required = float(criteria.get('amount', 0))
                current = float(player.total_mined_advc)
                return {
                    'percentage': min(100, int((current / required) * 100)) if required > 0 else 0,
                    'current': current,
                    'required': required
                }

            elif criteria_type == 'mining_events':
                required = criteria.get('count', 0)
                current = player.mining_events.count()
                return {
                    'percentage': min(100, int((current / required) * 100)) if required > 0 else 0,
                    'current': current,
                    'required': required
                }

            elif criteria_type == 'total_ap':
                required = criteria.get('amount', 0)
                current = player.total_ap
                return {
                    'percentage': min(100, int((current / required) * 100)) if required > 0 else 0,
                    'current': current,
                    'required': required
                }

            else:
                return {'percentage': 0}

        except Exception:
            return {'percentage': 0}


# Singleton instance
_achievement_service = None


def get_achievement_service(app=None, socketio=None):
    """Get or create the achievement service singleton."""
    global _achievement_service
    if _achievement_service is None and app:
        _achievement_service = AchievementService(app, socketio)
    return _achievement_service
