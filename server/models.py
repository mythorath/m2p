"""
Database models for M2P (Mine to Play) achievement system
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Player(Base):
    """Player model - stores user information and mining stats"""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True)
    wallet_address = Column(String(100), unique=True, nullable=False, index=True)

    # Mining statistics
    total_mined = Column(Float, default=0.0)
    total_ap = Column(Integer, default=0)  # Achievement Points

    # Streak tracking
    last_mining_date = Column(DateTime, nullable=True)
    consecutive_mining_days = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional stats for achievements
    total_mining_events = Column(Integer, default=0)
    unique_pools_mined = Column(JSON, default=list)  # List of pool IDs
    highest_leaderboard_rank = Column(Integer, nullable=True)

    # Relationships
    achievements = relationship('PlayerAchievement', back_populates='player', cascade='all, delete-orphan')
    mining_history = relationship('MiningEvent', back_populates='player', cascade='all, delete-orphan')
    daily_stats = relationship('DailyMiningStats', back_populates='player', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Player {self.username} (AP: {self.total_ap})>'


class Achievement(Base):
    """Achievement definitions - the master list of all achievements"""
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    achievement_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(10), nullable=False)
    ap_reward = Column(Integer, nullable=False)

    # Condition for unlocking
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(Float, nullable=False)

    # Metadata
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    category = Column(String(50), default='general')
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player_achievements = relationship('PlayerAchievement', back_populates='achievement', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Achievement {self.name} ({self.ap_reward} AP)>'


class PlayerAchievement(Base):
    """Junction table tracking which achievements players have unlocked"""
    __tablename__ = 'player_achievements'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)

    # Progress tracking
    progress = Column(Float, default=0.0)  # Current progress (0.0 - 1.0)
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)

    # Indexes for faster queries
    __table_args__ = (
        Index('ix_player_achievement', 'player_id', 'achievement_id', unique=True),
    )

    # Relationships
    player = relationship('Player', back_populates='achievements')
    achievement = relationship('Achievement', back_populates='player_achievements')

    def __repr__(self):
        status = 'Unlocked' if self.unlocked else f'{self.progress*100:.1f}%'
        return f'<PlayerAchievement Player:{self.player_id} Achievement:{self.achievement_id} {status}>'


class MiningEvent(Base):
    """Individual mining events for tracking history"""
    __tablename__ = 'mining_events'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    amount_mined = Column(Float, nullable=False)
    pool_id = Column(String(50), nullable=False)
    pool_name = Column(String(100), nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    player = relationship('Player', back_populates='mining_history')

    def __repr__(self):
        return f'<MiningEvent {self.amount_mined} ADVC from {self.pool_name}>'


class DailyMiningStats(Base):
    """Daily aggregated mining statistics"""
    __tablename__ = 'daily_mining_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    date = Column(DateTime, nullable=False, index=True)
    total_mined = Column(Float, default=0.0)
    mining_events_count = Column(Integer, default=0)
    unique_pools = Column(JSON, default=list)

    # Indexes
    __table_args__ = (
        Index('ix_player_date', 'player_id', 'date', unique=True),
    )

    # Relationships
    player = relationship('Player', back_populates='daily_stats')

    def __repr__(self):
        return f'<DailyStats Player:{self.player_id} {self.date.date()} {self.total_mined} ADVC>'


class Leaderboard(Base):
    """Leaderboard snapshot for tracking rankings"""
    __tablename__ = 'leaderboard'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)

    rank = Column(Integer, nullable=False)
    category = Column(String(50), default='total_mined')  # total_mined, total_ap, etc.
    value = Column(Float, nullable=False)

    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)

    # Indexes
    __table_args__ = (
        Index('ix_category_rank', 'category', 'rank'),
    )

    def __repr__(self):
        return f'<Leaderboard Rank:{self.rank} Player:{self.player_id} {self.category}>'
