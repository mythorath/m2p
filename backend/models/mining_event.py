"""Mining event model."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class MiningEvent(Base):
    """Mining event model - tracks individual mining activities."""

    __tablename__ = "mining_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Mining data
    advc_mined = Column(Float, nullable=False)
    ap_earned = Column(Integer, default=0)

    # Event metadata
    event_type = Column(String(50), default="mining")  # mining, bonus, achievement, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="mining_events")

    def __repr__(self):
        return f"<MiningEvent user_id={self.user_id} advc={self.advc_mined}>"
