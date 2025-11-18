"""
Database models for the M2P (Mining to Play) system.

This module defines all database models including:
- Player: User accounts and wallet information
- MiningEvent: Record of all mining rewards
- Achievement: Available achievements in the system
- PlayerAchievement: Unlocked achievements per player
- Purchase: AP spending history
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import random

db = SQLAlchemy()


class Player(db.Model):
    """
    Player model representing a user in the system.

    Attributes:
        wallet_address: Unique Advancecoin wallet address (primary key)
        display_name: Player's chosen display name
        verified: Whether player has completed wallet verification
        challenge_amount: Unique verification amount for this player
        challenge_expires_at: When the verification challenge expires
        total_ap: Lifetime accumulated Action Points
        spent_ap: Total AP spent on purchases
        total_mined_advc: Total Advancecoin mined across all events
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = 'players'

    wallet_address = db.Column(db.String(34), primary_key=True)
    display_name = db.Column(db.String(50), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    challenge_amount = db.Column(db.Numeric(10, 4), nullable=True)
    challenge_expires_at = db.Column(db.DateTime, nullable=True)
    total_ap = db.Column(db.Integer, default=0, nullable=False)
    spent_ap = db.Column(db.Integer, default=0, nullable=False)
    total_mined_advc = db.Column(db.Numeric(20, 8), default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    mining_events = db.relationship('MiningEvent', back_populates='player', lazy='dynamic')
    achievements = db.relationship('PlayerAchievement', back_populates='player', lazy='dynamic')
    purchases = db.relationship('Purchase', back_populates='player', lazy='dynamic')

    def __repr__(self):
        return f'<Player {self.display_name} ({self.wallet_address})>'

    @property
    def available_ap(self):
        """Calculate available AP (total - spent)."""
        return self.total_ap - self.spent_ap

    def to_dict(self, include_events=False, include_achievements=False):
        """
        Convert player to dictionary representation.

        Args:
            include_events: Whether to include recent mining events
            include_achievements: Whether to include achievement summary

        Returns:
            Dictionary representation of player
        """
        data = {
            'wallet_address': self.wallet_address,
            'display_name': self.display_name,
            'verified': self.verified,
            'total_ap': self.total_ap,
            'spent_ap': self.spent_ap,
            'available_ap': self.available_ap,
            'total_mined_advc': float(self.total_mined_advc),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_events:
            recent_events = self.mining_events.order_by(MiningEvent.timestamp.desc()).limit(10).all()
            data['recent_events'] = [event.to_dict() for event in recent_events]

        if include_achievements:
            unlocked_count = self.achievements.count()
            data['achievements_unlocked'] = unlocked_count

        return data


class MiningEvent(db.Model):
    """
    MiningEvent model representing a mining reward event.

    Attributes:
        id: Auto-incrementing primary key
        wallet_address: Foreign key to Player
        amount_advc: Amount of ADVC mined
        ap_awarded: Action Points awarded for this event
        pool: Mining pool name/identifier
        timestamp: When the mining event occurred
    """
    __tablename__ = 'mining_events'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    amount_advc = db.Column(db.Numeric(20, 8), nullable=False)
    ap_awarded = db.Column(db.Integer, nullable=False)
    pool = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='mining_events')

    def __repr__(self):
        return f'<MiningEvent {self.wallet_address} {self.amount_advc} ADVC>'

    def to_dict(self):
        """Convert mining event to dictionary representation."""
        return {
            'id': self.id,
            'amount_advc': float(self.amount_advc),
            'ap_awarded': self.ap_awarded,
            'pool': self.pool,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class Achievement(db.Model):
    """
    Achievement model representing available achievements.

    Attributes:
        id: Auto-incrementing primary key
        name: Achievement name
        description: Achievement description
        ap_reward: AP rewarded when unlocked
        icon: Icon identifier/URL
        created_at: When achievement was created
    """
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    ap_reward = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player_achievements = db.relationship('PlayerAchievement', back_populates='achievement', lazy='dynamic')

    def __repr__(self):
        return f'<Achievement {self.name}>'

    def to_dict(self, player_wallet=None):
        """
        Convert achievement to dictionary representation.

        Args:
            player_wallet: Optional wallet address to check unlock status

        Returns:
            Dictionary representation of achievement
        """
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ap_reward': self.ap_reward,
            'icon': self.icon,
        }

        if player_wallet:
            player_achievement = self.player_achievements.filter_by(
                wallet_address=player_wallet
            ).first()
            data['unlocked'] = player_achievement is not None
            if player_achievement:
                data['unlocked_at'] = player_achievement.unlocked_at.isoformat()

        return data


class PlayerAchievement(db.Model):
    """
    PlayerAchievement model representing unlocked achievements per player.

    Attributes:
        id: Auto-incrementing primary key
        wallet_address: Foreign key to Player
        achievement_id: Foreign key to Achievement
        unlocked_at: When the achievement was unlocked
    """
    __tablename__ = 'player_achievements'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='achievements')
    achievement = db.relationship('Achievement', back_populates='player_achievements')

    # Ensure a player can only unlock each achievement once
    __table_args__ = (
        db.UniqueConstraint('wallet_address', 'achievement_id', name='unique_player_achievement'),
    )

    def __repr__(self):
        return f'<PlayerAchievement {self.wallet_address} - Achievement {self.achievement_id}>'

    def to_dict(self):
        """Convert player achievement to dictionary representation."""
        return {
            'achievement_id': self.achievement_id,
            'achievement_name': self.achievement.name,
            'achievement_description': self.achievement.description,
            'ap_reward': self.achievement.ap_reward,
            'icon': self.achievement.icon,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
        }


class Purchase(db.Model):
    """
    Purchase model representing AP spending history.

    Attributes:
        id: Auto-incrementing primary key
        wallet_address: Foreign key to Player
        amount: AP spent
        item_id: Identifier of item purchased
        item_name: Name of item purchased
        timestamp: When the purchase occurred
    """
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='purchases')

    def __repr__(self):
        return f'<Purchase {self.wallet_address} - {self.amount} AP for {self.item_id}>'

    def to_dict(self):
        """Convert purchase to dictionary representation."""
        return {
            'id': self.id,
            'amount': self.amount,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


def generate_challenge_amount():
    """
    Generate a unique verification amount between 1.5000 and 1.9999 ADVC.

    Returns:
        Decimal: Random amount with 4 decimal places
    """
    # Generate amount between 1.5000 and 1.9999
    amount = 1.5 + (random.random() * 0.5)
    return round(amount, 4)
