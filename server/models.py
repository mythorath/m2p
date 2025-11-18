"""
Database models for M2P Wallet Verification System
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Player(Base):
    """Player model for wallet verification and AP tracking"""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_address = Column(String(128), unique=True, nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    verification_amount = Column(Float, nullable=True)
    verification_requested_at = Column(DateTime, nullable=True)
    verification_tx_hash = Column(String(128), nullable=True)
    verification_completed_at = Column(DateTime, nullable=True)
    total_ap = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Player(wallet={self.wallet_address}, verified={self.verified}, ap={self.total_ap})>"

    def to_dict(self):
        """Convert player to dictionary"""
        return {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'verified': self.verified,
            'verification_amount': self.verification_amount,
            'verification_requested_at': self.verification_requested_at.isoformat() if self.verification_requested_at else None,
            'verification_tx_hash': self.verification_tx_hash,
            'verification_completed_at': self.verification_completed_at.isoformat() if self.verification_completed_at else None,
            'total_ap': self.total_ap,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VerificationLog(Base):
    """Log of verification attempts and results"""
    __tablename__ = 'verification_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False, index=True)
    wallet_address = Column(String(128), nullable=False)
    verification_method = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)  # success, failed, expired, error
    tx_hash = Column(String(128), nullable=True)
    amount = Column(Float, nullable=True)
    ap_credited = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VerificationLog(wallet={self.wallet_address}, method={self.verification_method}, status={self.status})>"
