"""
Achievement management system for M2P (Mine to Play)
Handles achievement checking, progress tracking, and unlocking
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from server.models import Player, Achievement, PlayerAchievement, DailyMiningStats
import logging

logger = logging.getLogger(__name__)


class AchievementManager:
    """Manages achievement checking and unlocking"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def check_achievements(self, player: Player) -> List[Dict]:
        """
        Check all achievements for a player and unlock any that are newly completed.
        Returns a list of newly unlocked achievements.

        Args:
            player: The Player object to check achievements for

        Returns:
            List of dicts containing newly unlocked achievement data
        """
        newly_unlocked = []

        # Get all achievements from database
        all_achievements = self.db.query(Achievement).all()

        for achievement in all_achievements:
            # Check if player already has this achievement
            player_achievement = self.db.query(PlayerAchievement).filter(
                PlayerAchievement.player_id == player.id,
                PlayerAchievement.achievement_id == achievement.id
            ).first()

            # Skip if already unlocked
            if player_achievement and player_achievement.unlocked:
                continue

            # Check condition based on type
            progress, is_unlocked = self._check_condition(
                player,
                achievement.condition_type,
                achievement.condition_value
            )

            # Create or update player achievement record
            if not player_achievement:
                player_achievement = PlayerAchievement(
                    player_id=player.id,
                    achievement_id=achievement.id,
                    progress=progress,
                    unlocked=is_unlocked
                )
                self.db.add(player_achievement)
            else:
                player_achievement.progress = progress
                player_achievement.unlocked = is_unlocked

            # If newly unlocked, award AP and record unlock time
            if is_unlocked and not player_achievement.unlocked_at:
                player_achievement.unlocked_at = datetime.utcnow()
                player.total_ap += achievement.ap_reward

                newly_unlocked.append({
                    'id': achievement.achievement_id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'ap_reward': achievement.ap_reward,
                    'category': achievement.category
                })

                logger.info(
                    f"Achievement unlocked! Player: {player.username}, "
                    f"Achievement: {achievement.name}, AP: {achievement.ap_reward}"
                )

        # Commit all changes
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error committing achievement updates: {e}")
            self.db.rollback()
            raise

        return newly_unlocked

    def _check_condition(self, player: Player, condition_type: str, condition_value: float) -> tuple:
        """
        Check if a specific condition is met for a player.

        Args:
            player: The Player object
            condition_type: Type of condition (e.g., 'total_mined', 'consecutive_days')
            condition_value: The value to check against

        Returns:
            Tuple of (progress: float, is_unlocked: bool)
            progress is 0.0-1.0 representing percentage complete
        """
        handlers = {
            'total_mined': self.check_total_mined,
            'consecutive_days': self.check_consecutive_days,
            'daily_mined': self.check_daily_mined,
            'unique_pools': self.check_unique_pools,
            'mining_events': self.check_mining_events,
            'leaderboard_rank': self.check_leaderboard_rank,
            'special': self.check_special
        }

        handler = handlers.get(condition_type)
        if not handler:
            logger.warning(f"Unknown condition type: {condition_type}")
            return 0.0, False

        return handler(player, condition_value)

    def check_total_mined(self, player: Player, target_value: float) -> tuple:
        """Check if player has mined enough total ADVC"""
        current_value = player.total_mined
        progress = min(current_value / target_value, 1.0)
        is_unlocked = current_value >= target_value
        return progress, is_unlocked

    def check_consecutive_days(self, player: Player, target_days: float) -> tuple:
        """Check if player has mined for consecutive days"""
        current_days = player.consecutive_mining_days
        progress = min(current_days / target_days, 1.0)
        is_unlocked = current_days >= target_days
        return progress, is_unlocked

    def check_daily_mined(self, player: Player, target_amount: float) -> tuple:
        """Check if player has mined target amount in a single day"""
        # Get the highest daily mining total
        max_daily = self.db.query(
            func.max(DailyMiningStats.total_mined)
        ).filter(
            DailyMiningStats.player_id == player.id
        ).scalar()

        current_value = max_daily or 0.0
        progress = min(current_value / target_amount, 1.0)
        is_unlocked = current_value >= target_amount
        return progress, is_unlocked

    def check_unique_pools(self, player: Player, target_count: float) -> tuple:
        """Check if player has mined on enough unique pools"""
        unique_pools = player.unique_pools_mined or []
        current_count = len(unique_pools)
        progress = min(current_count / target_count, 1.0)
        is_unlocked = current_count >= target_count
        return progress, is_unlocked

    def check_mining_events(self, player: Player, target_count: float) -> tuple:
        """Check if player has completed enough mining events"""
        current_count = player.total_mining_events
        progress = min(current_count / target_count, 1.0)
        is_unlocked = current_count >= target_count
        return progress, is_unlocked

    def check_leaderboard_rank(self, player: Player, target_rank: float) -> tuple:
        """
        Check if player has reached target leaderboard rank.
        Lower rank number is better (1 is best).
        """
        current_rank = player.highest_leaderboard_rank

        if current_rank is None:
            return 0.0, False

        # For leaderboard, being at rank 1 when target is 10 = 100% progress
        # Being at rank 100 when target is 10 = 0% progress
        # Progress calculation: if current <= target, then 100%, else scale down
        if current_rank <= target_rank:
            progress = 1.0
            is_unlocked = True
        else:
            # Scale progress - e.g., rank 50 for target 10 = 20% progress
            progress = max(0.0, 1.0 - (current_rank - target_rank) / 100.0)
            is_unlocked = False

        return progress, is_unlocked

    def check_special(self, player: Player, condition_value: float) -> tuple:
        """
        Check special achievements (manually awarded or time-based).
        For now, returns False - these should be manually triggered.
        """
        # Special achievements are typically awarded manually
        # Could check player.created_at for early adopter, etc.
        return 0.0, False

    def get_player_achievements(self, player: Player, include_locked: bool = True) -> List[Dict]:
        """
        Get all achievements for a player with their progress.

        Args:
            player: The Player object
            include_locked: Whether to include locked achievements

        Returns:
            List of achievement dicts with progress information
        """
        query = self.db.query(Achievement, PlayerAchievement).outerjoin(
            PlayerAchievement,
            (Achievement.id == PlayerAchievement.achievement_id) &
            (PlayerAchievement.player_id == player.id)
        )

        if not include_locked:
            query = query.filter(Achievement.is_hidden == False)

        results = []
        for achievement, player_achievement in query.all():
            # Skip hidden achievements unless unlocked
            if achievement.is_hidden and (not player_achievement or not player_achievement.unlocked):
                continue

            achievement_data = {
                'id': achievement.achievement_id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'ap_reward': achievement.ap_reward,
                'category': achievement.category,
                'unlocked': player_achievement.unlocked if player_achievement else False,
                'progress': player_achievement.progress if player_achievement else 0.0,
                'unlocked_at': player_achievement.unlocked_at.isoformat() if (
                    player_achievement and player_achievement.unlocked_at
                ) else None
            }
            results.append(achievement_data)

        # Sort by category and sort_order
        results.sort(key=lambda x: (x['category'], x.get('sort_order', 999)))

        return results

    def get_achievement_stats(self, player: Player) -> Dict:
        """
        Get achievement statistics for a player.

        Returns:
            Dict with total achievements, unlocked count, completion percentage, etc.
        """
        total_achievements = self.db.query(Achievement).filter(
            Achievement.is_hidden == False
        ).count()

        unlocked_count = self.db.query(PlayerAchievement).filter(
            PlayerAchievement.player_id == player.id,
            PlayerAchievement.unlocked == True
        ).count()

        completion_percentage = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0

        return {
            'total_achievements': total_achievements,
            'unlocked': unlocked_count,
            'locked': total_achievements - unlocked_count,
            'completion_percentage': round(completion_percentage, 1),
            'total_ap': player.total_ap
        }

    def award_special_achievement(self, player: Player, achievement_id: str) -> Optional[Dict]:
        """
        Manually award a special achievement to a player.

        Args:
            player: The Player object
            achievement_id: The achievement ID to award

        Returns:
            Dict with achievement data if successfully awarded, None otherwise
        """
        achievement = self.db.query(Achievement).filter(
            Achievement.achievement_id == achievement_id
        ).first()

        if not achievement:
            logger.warning(f"Achievement not found: {achievement_id}")
            return None

        # Check if already unlocked
        player_achievement = self.db.query(PlayerAchievement).filter(
            PlayerAchievement.player_id == player.id,
            PlayerAchievement.achievement_id == achievement.id
        ).first()

        if player_achievement and player_achievement.unlocked:
            logger.info(f"Player {player.username} already has achievement {achievement_id}")
            return None

        # Create or update achievement
        if not player_achievement:
            player_achievement = PlayerAchievement(
                player_id=player.id,
                achievement_id=achievement.id,
                progress=1.0,
                unlocked=True,
                unlocked_at=datetime.utcnow()
            )
            self.db.add(player_achievement)
        else:
            player_achievement.progress = 1.0
            player_achievement.unlocked = True
            player_achievement.unlocked_at = datetime.utcnow()

        # Award AP
        player.total_ap += achievement.ap_reward

        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error awarding special achievement: {e}")
            self.db.rollback()
            raise

        return {
            'id': achievement.achievement_id,
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'ap_reward': achievement.ap_reward,
            'category': achievement.category
        }
