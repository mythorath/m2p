"""User model."""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """User/Player model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)

    # Mining stats
    total_mined_advc = Column(Float, default=0.0)
    total_ap = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_mining_event = Column(DateTime, nullable=True)

    # Relationships
    mining_events = relationship("MiningEvent", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("PlayerAchievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.display_name or self.wallet_address}>"

    @property
    def wallet_truncated(self):
        """Return truncated wallet address."""
        if not self.wallet_address:
            return ""
        return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"

    @property
    def mining_hours(self):
        """Calculate hours since registration."""
        if not self.created_at:
            return 0
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600

    @property
    def efficiency(self):
        """Calculate ADVC per hour."""
        hours = self.mining_hours
        if hours == 0:
            return 0
        return self.total_mined_advc / hours
