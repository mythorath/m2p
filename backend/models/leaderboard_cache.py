"""Leaderboard cache model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Index
from datetime import datetime
from database import Base


class LeaderboardCache(Base):
    """Leaderboard cache model - stores pre-computed rankings."""

    __tablename__ = "leaderboard_cache"

    id = Column(Integer, primary_key=True, index=True)

    # Ranking data
    period = Column(String(50), nullable=False, index=True)  # all_time, this_week, today, efficiency
    rank = Column(Integer, nullable=False, index=True)
    previous_rank = Column(Integer, nullable=True)

    # User data (denormalized for performance)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_address = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)

    # Stats
    total_mined_advc = Column(Float, nullable=False)
    total_ap = Column(Integer, default=0)
    period_score = Column(Float, nullable=False)  # The score used for ranking this period

    # Metadata
    last_mining_event = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Additional data
    extra_data = Column(JSON, nullable=True)  # For storing additional period-specific data

    __table_args__ = (
        Index('idx_period_rank', 'period', 'rank'),
        Index('idx_period_user', 'period', 'user_id'),
    )

    def __repr__(self):
        return f"<LeaderboardCache period={self.period} rank={self.rank} user_id={self.user_id}>"

    @property
    def rank_change(self):
        """Calculate rank change."""
        if self.previous_rank is None:
            return "new"
        change = self.previous_rank - self.rank
        if change > 0:
            return f"up_{change}"
        elif change < 0:
            return f"down_{abs(change)}"
        return "same"
