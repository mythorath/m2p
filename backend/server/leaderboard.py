"""Leaderboard management system."""
import json
import redis
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session

from models.user import User
from models.mining_event import MiningEvent
from models.leaderboard_cache import LeaderboardCache
from config import settings


class LeaderboardManager:
    """Manages leaderboard calculations, caching, and updates."""

    PERIODS = ["all_time", "this_week", "today", "efficiency"]

    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        """Initialize leaderboard manager.

        Args:
            db: Database session
            redis_client: Optional Redis client for caching
        """
        self.db = db
        self.redis = redis_client
        self.cache_ttl = settings.LEADERBOARD_CACHE_TTL
        self.top_limit = settings.LEADERBOARD_TOP_LIMIT

    def _get_redis_key(self, period: str, page: int = 0) -> str:
        """Generate Redis cache key."""
        return f"leaderboard:{period}:page:{page}"

    def _get_period_filter(self, period: str) -> Optional[datetime]:
        """Get datetime filter for the period."""
        now = datetime.utcnow()
        if period == "today":
            return now - timedelta(days=1)
        elif period == "this_week":
            return now - timedelta(days=7)
        return None

    def calculate_rankings(self, period: str, limit: int = None) -> List[Dict[str, Any]]:
        """Calculate rankings for a specific period.

        Args:
            period: One of 'all_time', 'this_week', 'today', 'efficiency'
            limit: Maximum number of ranks to return (default: LEADERBOARD_TOP_LIMIT)

        Returns:
            List of ranking dictionaries
        """
        if period not in self.PERIODS:
            raise ValueError(f"Invalid period: {period}. Must be one of {self.PERIODS}")

        limit = limit or self.top_limit

        if period == "all_time":
            return self._calculate_all_time(limit)
        elif period == "this_week":
            return self._calculate_time_period(limit, days=7)
        elif period == "today":
            return self._calculate_time_period(limit, days=1)
        elif period == "efficiency":
            return self._calculate_efficiency(limit)

    def _calculate_all_time(self, limit: int) -> List[Dict[str, Any]]:
        """Calculate all-time rankings based on total_mined_advc."""
        users = (
            self.db.query(User)
            .filter(User.total_mined_advc > 0)
            .order_by(desc(User.total_mined_advc))
            .limit(limit)
            .all()
        )

        rankings = []
        for rank, user in enumerate(users, start=1):
            rankings.append({
                "rank": rank,
                "user_id": user.id,
                "wallet_address": user.wallet_address,
                "display_name": user.display_name,
                "is_verified": user.is_verified,
                "total_mined_advc": user.total_mined_advc,
                "total_ap": user.total_ap,
                "last_mining_event": user.last_mining_event,
                "period_score": user.total_mined_advc,
            })

        return rankings

    def _calculate_time_period(self, limit: int, days: int) -> List[Dict[str, Any]]:
        """Calculate rankings for a time period based on mining events."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Aggregate mining events for the period
        results = (
            self.db.query(
                MiningEvent.user_id,
                func.sum(MiningEvent.advc_mined).label("period_advc"),
                func.sum(MiningEvent.ap_earned).label("period_ap"),
                func.max(MiningEvent.timestamp).label("last_event"),
            )
            .filter(MiningEvent.timestamp >= cutoff)
            .group_by(MiningEvent.user_id)
            .order_by(desc("period_advc"))
            .limit(limit)
            .all()
        )

        # Join with user data
        rankings = []
        for rank, result in enumerate(results, start=1):
            user = self.db.query(User).filter(User.id == result.user_id).first()
            if user:
                rankings.append({
                    "rank": rank,
                    "user_id": user.id,
                    "wallet_address": user.wallet_address,
                    "display_name": user.display_name,
                    "is_verified": user.is_verified,
                    "total_mined_advc": user.total_mined_advc,
                    "total_ap": user.total_ap,
                    "last_mining_event": result.last_event,
                    "period_score": float(result.period_advc),
                })

        return rankings

    def _calculate_efficiency(self, limit: int) -> List[Dict[str, Any]]:
        """Calculate efficiency rankings (ADVC per hour)."""
        users = (
            self.db.query(User)
            .filter(User.total_mined_advc > 0)
            .all()
        )

        # Calculate efficiency for each user
        user_efficiency = []
        for user in users:
            efficiency = user.efficiency
            if efficiency > 0:  # Only include users with positive efficiency
                user_efficiency.append({
                    "user": user,
                    "efficiency": efficiency,
                })

        # Sort by efficiency
        user_efficiency.sort(key=lambda x: x["efficiency"], reverse=True)

        # Build rankings
        rankings = []
        for rank, item in enumerate(user_efficiency[:limit], start=1):
            user = item["user"]
            rankings.append({
                "rank": rank,
                "user_id": user.id,
                "wallet_address": user.wallet_address,
                "display_name": user.display_name,
                "is_verified": user.is_verified,
                "total_mined_advc": user.total_mined_advc,
                "total_ap": user.total_ap,
                "last_mining_event": user.last_mining_event,
                "period_score": item["efficiency"],
            })

        return rankings

    def update_leaderboard_cache(self, period: str = None) -> Dict[str, int]:
        """Update leaderboard cache in database.

        Args:
            period: Specific period to update, or None for all periods

        Returns:
            Dictionary with update counts per period
        """
        periods = [period] if period else self.PERIODS
        update_counts = {}

        for p in periods:
            rankings = self.calculate_rankings(p)

            # Get previous rankings for rank change tracking
            previous_rankings = {}
            prev_cache = (
                self.db.query(LeaderboardCache)
                .filter(LeaderboardCache.period == p)
                .all()
            )
            for cache_entry in prev_cache:
                previous_rankings[cache_entry.user_id] = cache_entry.rank

            # Delete old cache entries for this period
            self.db.query(LeaderboardCache).filter(
                LeaderboardCache.period == p
            ).delete()

            # Insert new cache entries
            for ranking in rankings:
                cache_entry = LeaderboardCache(
                    period=p,
                    rank=ranking["rank"],
                    previous_rank=previous_rankings.get(ranking["user_id"]),
                    user_id=ranking["user_id"],
                    wallet_address=ranking["wallet_address"],
                    display_name=ranking["display_name"],
                    is_verified=ranking["is_verified"],
                    total_mined_advc=ranking["total_mined_advc"],
                    total_ap=ranking["total_ap"],
                    period_score=ranking["period_score"],
                    last_mining_event=ranking["last_mining_event"],
                )
                self.db.add(cache_entry)

            self.db.commit()
            update_counts[p] = len(rankings)

            # Update Redis cache if available
            if self.redis:
                self._update_redis_cache(p, rankings)

        return update_counts

    def _update_redis_cache(self, period: str, rankings: List[Dict[str, Any]]):
        """Update Redis cache for a period."""
        page_size = 100
        for page in range(0, len(rankings), page_size):
            page_rankings = rankings[page:page + page_size]
            key = self._get_redis_key(period, page // page_size)
            self.redis.setex(
                key,
                self.cache_ttl,
                json.dumps(page_rankings, default=str)
            )

    def get_leaderboard(
        self,
        period: str,
        limit: int = 100,
        offset: int = 0,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Get leaderboard for a period.

        Args:
            period: Leaderboard period
            limit: Number of entries to return
            offset: Offset for pagination
            use_cache: Whether to use cached data

        Returns:
            List of leaderboard entries
        """
        if period not in self.PERIODS:
            raise ValueError(f"Invalid period: {period}")

        # Try Redis cache first
        if use_cache and self.redis:
            page = offset // 100
            key = self._get_redis_key(period, page)
            cached = self.redis.get(key)
            if cached:
                all_rankings = json.loads(cached)
                start = offset % 100
                return all_rankings[start:start + limit]

        # Try database cache
        if use_cache:
            cache_entries = (
                self.db.query(LeaderboardCache)
                .filter(LeaderboardCache.period == period)
                .order_by(LeaderboardCache.rank)
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Check if cache is fresh (less than cache_ttl old)
            if cache_entries:
                latest_update = max(entry.updated_at for entry in cache_entries)
                age = (datetime.utcnow() - latest_update).total_seconds()

                if age < self.cache_ttl:
                    return [self._cache_entry_to_dict(entry) for entry in cache_entries]

        # Recalculate if cache miss or stale
        all_rankings = self.calculate_rankings(period)
        return all_rankings[offset:offset + limit]

    def get_player_rank(
        self,
        wallet_address: str,
        period: str,
        context: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Get player's rank and nearby rankings.

        Args:
            wallet_address: Player's wallet address
            period: Leaderboard period
            context: Number of positions to show above and below

        Returns:
            Dictionary with player rank and nearby rankings, or None if not ranked
        """
        # Get player's rank from cache
        cache_entry = (
            self.db.query(LeaderboardCache)
            .filter(
                and_(
                    LeaderboardCache.period == period,
                    LeaderboardCache.wallet_address == wallet_address
                )
            )
            .first()
        )

        if not cache_entry or cache_entry.rank > self.top_limit:
            return None

        player_rank = cache_entry.rank

        # Get nearby rankings
        nearby = (
            self.db.query(LeaderboardCache)
            .filter(
                and_(
                    LeaderboardCache.period == period,
                    LeaderboardCache.rank >= max(1, player_rank - context),
                    LeaderboardCache.rank <= player_rank + context
                )
            )
            .order_by(LeaderboardCache.rank)
            .all()
        )

        return {
            "player_rank": player_rank,
            "previous_rank": cache_entry.previous_rank,
            "rank_change": cache_entry.rank_change,
            "period_score": cache_entry.period_score,
            "nearby_rankings": [self._cache_entry_to_dict(entry) for entry in nearby],
        }

    def _cache_entry_to_dict(self, entry: LeaderboardCache) -> Dict[str, Any]:
        """Convert cache entry to dictionary."""
        return {
            "rank": entry.rank,
            "previous_rank": entry.previous_rank,
            "rank_change": entry.rank_change,
            "user_id": entry.user_id,
            "wallet_address": entry.wallet_address,
            "wallet_truncated": f"{entry.wallet_address[:6]}...{entry.wallet_address[-4:]}",
            "display_name": entry.display_name,
            "is_verified": entry.is_verified,
            "total_mined_advc": entry.total_mined_advc,
            "total_ap": entry.total_ap,
            "period_score": entry.period_score,
            "last_mining_event": entry.last_mining_event.isoformat() if entry.last_mining_event else None,
        }

    def on_mining_event(self, user_id: int) -> List[Dict[str, Any]]:
        """Handle mining event and check for rank changes.

        Args:
            user_id: User ID who mined

        Returns:
            List of rank changes that occurred
        """
        rank_changes = []

        # Check rank changes in all periods
        for period in self.PERIODS:
            old_entry = (
                self.db.query(LeaderboardCache)
                .filter(
                    and_(
                        LeaderboardCache.period == period,
                        LeaderboardCache.user_id == user_id
                    )
                )
                .first()
            )

            old_rank = old_entry.rank if old_entry else None

            # Recalculate rankings (in production, you might do this less frequently)
            # For now, we'll just note that a change occurred
            if old_rank:
                rank_changes.append({
                    "period": period,
                    "user_id": user_id,
                    "old_rank": old_rank,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return rank_changes


def get_leaderboard_manager(db: Session) -> LeaderboardManager:
    """Get leaderboard manager instance.

    Args:
        db: Database session

    Returns:
        LeaderboardManager instance
    """
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()  # Test connection
    except Exception:
        redis_client = None

    return LeaderboardManager(db, redis_client)
