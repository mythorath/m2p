"""Achievement models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Achievement(Base):
    """Achievement definition model."""

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="general")  # general, leaderboard, mining, etc.

    # Requirements
    requirement_type = Column(String(50), nullable=False)  # rank, mining_total, streak, etc.
    requirement_value = Column(String(255), nullable=True)  # JSON string of requirements

    # Rewards
    ap_reward = Column(Integer, default=0)

    # Metadata
    icon = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player_achievements = relationship("PlayerAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement {self.code}>"


class PlayerAchievement(Base):
    """Player achievement - tracks which achievements players have earned."""

    __tablename__ = "player_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)

    # Achievement data
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress = Column(Integer, default=100)  # Percentage completion

    # Metadata
    extra_data = Column(Text, nullable=True)  # JSON string for additional data

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="player_achievements")

    def __repr__(self):
        return f"<PlayerAchievement user_id={self.user_id} achievement_id={self.achievement_id}>"
