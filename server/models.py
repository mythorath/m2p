"""
SQLAlchemy models for Mine-to-Play game.

This module defines the database schema for tracking players, mining events,
pool snapshots, achievements, and their relationships.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, UniqueConstraint, Numeric, func

db = SQLAlchemy()


class Player(db.Model):
    """
    Represents a player in the Mine-to-Play game.

    Players are identified by their wallet address and earn Achievement Points (AP)
    through mining ADVC cryptocurrency. Players must verify their wallet by sending
    a small amount of ADVC.

    Attributes:
        id: Primary key
        wallet_address: Unique blockchain wallet address (64 chars max)
        display_name: Optional display name for the player (32 chars max)
        verified: Whether the player has verified their wallet
        verification_amount: Amount of ADVC sent for verification
        verification_tx_hash: Transaction hash of verification payment
        total_ap: Total Achievement Points earned
        spent_ap: Achievement Points spent on rewards
        total_mined_advc: Total ADVC mined across all pools
        created_at: Account creation timestamp
        last_seen_at: Last activity timestamp
    """
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(64), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(32), nullable=True)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_amount = db.Column(Numeric(18, 8), nullable=True)
    verification_tx_hash = db.Column(db.String(128), nullable=True)
    total_ap = db.Column(db.Integer, default=0, nullable=False)
    spent_ap = db.Column(db.Integer, default=0, nullable=False)
    total_mined_advc = db.Column(Numeric(18, 8), default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    mining_events = db.relationship('MiningEvent', back_populates='player',
                                   lazy='dynamic', cascade='all, delete-orphan')
    pool_snapshots = db.relationship('PoolSnapshot', back_populates='player',
                                    lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('PlayerAchievement', back_populates='player',
                                  lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """
        Serialize player data for API responses.

        Returns:
            dict: Player data including all public fields and computed values
        """
        return {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'display_name': self.display_name,
            'verified': self.verified,
            'total_ap': self.total_ap,
            'available_ap': self.total_ap - self.spent_ap,
            'spent_ap': self.spent_ap,
            'total_mined_advc': float(self.total_mined_advc),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None,
            'rank': self.calculate_rank()
        }

    def calculate_rank(self):
        """
        Calculate player's position on the leaderboard.

        Rank is based on total_ap in descending order. Returns None if player
        has no AP or hasn't participated yet.

        Returns:
            int or None: Player's rank (1-indexed), or None if not ranked
        """
        if self.total_ap == 0:
            return None

        # Count players with more AP than current player
        rank = db.session.query(func.count(Player.id))\
            .filter(Player.total_ap > self.total_ap)\
            .scalar()

        return rank + 1 if rank is not None else 1

    def __repr__(self):
        return f'<Player {self.wallet_address[:10]}... AP:{self.total_ap}>'


class MiningEvent(db.Model):
    """
    Records individual mining payouts detected from pool APIs.

    Each event represents a payout from a mining pool to a player's wallet.
    Events are processed to award Achievement Points based on the amount mined.

    Attributes:
        id: Primary key
        player_id: Foreign key to Player
        pool_name: Name of the mining pool (e.g., 'cpu-pool', 'rplant', 'zpool')
        amount_advc: Amount of ADVC paid out in this event
        ap_awarded: Achievement Points awarded for this event
        detected_at: When this payout was detected by the system
    """
    __tablename__ = 'mining_events'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    pool_name = db.Column(db.String(32), nullable=False)
    amount_advc = db.Column(Numeric(18, 8), nullable=False)
    ap_awarded = db.Column(db.Integer, nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='mining_events')

    # Index for efficient queries by player and time
    __table_args__ = (
        Index('idx_player_detected', 'player_id', 'detected_at'),
    )

    def to_dict(self):
        """Serialize mining event for API responses."""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'pool_name': self.pool_name,
            'amount_advc': float(self.amount_advc),
            'ap_awarded': self.ap_awarded,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }

    def __repr__(self):
        return f'<MiningEvent player:{self.player_id} pool:{self.pool_name} amount:{self.amount_advc}>'


class PoolSnapshot(db.Model):
    """
    Stores periodic snapshots of cumulative payouts from mining pools.

    Snapshots are taken at regular intervals to track the total amount paid
    to each player by each pool. This allows detection of new payouts by
    comparing snapshots.

    Attributes:
        id: Primary key
        player_id: Foreign key to Player
        pool_name: Name of the mining pool
        paid_amount: Cumulative amount paid to player at snapshot time
        snapshot_at: Timestamp when snapshot was taken
    """
    __tablename__ = 'pool_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    pool_name = db.Column(db.String(32), nullable=False)
    paid_amount = db.Column(Numeric(18, 8), nullable=False)
    snapshot_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='pool_snapshots')

    # Ensure only one snapshot per player/pool/time combination
    __table_args__ = (
        UniqueConstraint('player_id', 'pool_name', 'snapshot_at',
                        name='uq_player_pool_snapshot'),
    )

    def to_dict(self):
        """Serialize pool snapshot for API responses."""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'pool_name': self.pool_name,
            'paid_amount': float(self.paid_amount),
            'snapshot_at': self.snapshot_at.isoformat() if self.snapshot_at else None
        }

    def __repr__(self):
        return f'<PoolSnapshot player:{self.player_id} pool:{self.pool_name} amount:{self.paid_amount}>'


class Achievement(db.Model):
    """
    Defines available achievements that players can unlock.

    Achievements reward players with AP for reaching milestones like total
    ADVC mined, consecutive mining days, or other game objectives.

    Attributes:
        id: Unique achievement identifier (e.g., 'first_mine', 'whale_100')
        name: Display name of the achievement
        description: Detailed description of how to unlock
        ap_reward: Achievement Points awarded when unlocked
        icon: Emoji or short icon representation
        condition_type: Type of condition (e.g., 'total_mined', 'consecutive_days')
        condition_value: Numeric threshold for unlocking
    """
    __tablename__ = 'achievements'

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ap_reward = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(8), nullable=True)
    condition_type = db.Column(db.String(32), nullable=False)
    condition_value = db.Column(db.Float, nullable=False)

    # Relationships
    player_achievements = db.relationship('PlayerAchievement', back_populates='achievement',
                                         lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """Serialize achievement for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ap_reward': self.ap_reward,
            'icon': self.icon,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value
        }

    def __repr__(self):
        return f'<Achievement {self.id}: {self.name}>'


class PlayerAchievement(db.Model):
    """
    Tracks which achievements have been unlocked by each player.

    This is a junction table between Player and Achievement with additional
    metadata about when the achievement was unlocked and progress toward
    multi-stage achievements.

    Attributes:
        player_id: Foreign key to Player (composite primary key)
        achievement_id: Foreign key to Achievement (composite primary key)
        unlocked_at: Timestamp when achievement was unlocked
        progress: Progress toward achievement (0.0 to 1.0 for multi-stage)
    """
    __tablename__ = 'player_achievements'

    player_id = db.Column(db.Integer, db.ForeignKey('players.id'),
                         primary_key=True, nullable=False)
    achievement_id = db.Column(db.String(32), db.ForeignKey('achievements.id'),
                              primary_key=True, nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    progress = db.Column(db.Float, default=0.0, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='achievements')
    achievement = db.relationship('Achievement', back_populates='player_achievements')

    def to_dict(self):
        """Serialize player achievement for API responses."""
        return {
            'player_id': self.player_id,
            'achievement_id': self.achievement_id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress': self.progress
        }

    def __repr__(self):
        return f'<PlayerAchievement player:{self.player_id} achievement:{self.achievement_id}>'
