"""Database models for the Pool Monitoring Service."""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Player(Base):
    """Player model representing a verified mining player."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    wallet_address = Column(String(255), unique=True, nullable=False, index=True)

    # Game stats
    total_ap = Column(Float, default=0.0, nullable=False)
    total_advc_mined = Column(Float, default=0.0, nullable=False)
    level = Column(Integer, default=1, nullable=False)

    # Account status
    verified = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_mining_event = Column(DateTime, nullable=True)

    # Relationships
    pool_snapshots = relationship("PoolSnapshot", back_populates="player", cascade="all, delete-orphan")
    mining_events = relationship("MiningEvent", back_populates="player", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Player(id={self.id}, username='{self.username}', wallet='{self.wallet_address}')>"


class PoolSnapshot(Base):
    """Snapshot of a player's mining pool statistics at a point in time."""

    __tablename__ = "pool_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    pool_name = Column(String(50), nullable=False)

    # Pool statistics
    total_hash = Column(Float, default=0.0)
    total_shares = Column(Float, default=0.0)
    immature = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    paid = Column(Float, default=0.0, nullable=False)  # Cumulative payouts (main tracking field)

    # Raw response (for debugging)
    raw_response = Column(String, nullable=True)

    # Timestamp
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    player = relationship("Player", back_populates="pool_snapshots")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_player_pool", "player_id", "pool_name"),
        Index("idx_snapshot_time", "snapshot_time"),
    )

    def __repr__(self):
        return f"<PoolSnapshot(player_id={self.player_id}, pool='{self.pool_name}', paid={self.paid})>"


class MiningEvent(Base):
    """Record of a detected mining reward/payout event."""

    __tablename__ = "mining_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    pool_name = Column(String(50), nullable=False)

    # Reward details
    advc_amount = Column(Float, nullable=False)  # Amount of ADVC paid out
    ap_awarded = Column(Float, nullable=False)  # AP awarded for this payout
    previous_paid = Column(Float, nullable=False)  # Previous cumulative paid amount
    current_paid = Column(Float, nullable=False)  # New cumulative paid amount

    # Event metadata
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed = Column(Boolean, default=False, nullable=False)
    notified = Column(Boolean, default=False, nullable=False)  # Whether player was notified via WebSocket

    # Relationships
    player = relationship("Player", back_populates="mining_events")

    # Indexes
    __table_args__ = (
        Index("idx_player_event_time", "player_id", "event_time"),
        Index("idx_event_time", "event_time"),
    )

    def __repr__(self):
        return f"<MiningEvent(player_id={self.player_id}, pool='{self.pool_name}', advc={self.advc_amount}, ap={self.ap_awarded})>"
