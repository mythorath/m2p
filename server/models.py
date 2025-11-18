"""
Database models for the M2P (Mining to Play) system.

This module defines all database models including:
- Player: User accounts and wallet information
- MiningEvent: Record of all mining rewards
- Achievement: Available achievements in the system
- PlayerAchievement: Unlocked achievements per player
- Purchase: AP spending history
- Dungeon: Dungeon configurations
- DungeonRun: Active and completed dungeon runs
- PlayerCharacter: RPG stats for players
- Gear: Equipment items (weapons, armor, accessories)
- PlayerInventory: Player's gear collection
- Monster: Enemy definitions
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import json
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
    total_advc = db.Column(db.Numeric(20, 8), default=0, nullable=False)  # Alias for compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    mining_events = db.relationship('MiningEvent', foreign_keys='MiningEvent.wallet_address', back_populates='player', lazy='dynamic')
    achievements = db.relationship('PlayerAchievement', back_populates='player', lazy='dynamic')
    purchases = db.relationship('Purchase', back_populates='player', lazy='dynamic')
    character = db.relationship('PlayerCharacter', back_populates='player', uselist=False)
    dungeon_runs = db.relationship('DungeonRun', back_populates='player', lazy='dynamic')
    inventory = db.relationship('PlayerInventory', back_populates='player', lazy='dynamic')

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
        player_wallet: Foreign key to Player
        amount_advc: Amount of ADVC mined
        ap_earned: Action Points awarded for this event
        pool_name: Mining pool name/identifier
        event_time: When the mining event occurred
        tx_hash: Transaction hash (if available)
    """
    __tablename__ = 'mining_events'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    amount_advc = db.Column(db.Numeric(20, 8), nullable=False)
    ap_awarded = db.Column(db.Integer, nullable=False)
    pool = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tx_hash = db.Column(db.String(128), nullable=True)

    # Relationships
    player = db.relationship('Player', back_populates='mining_events')

    # Property aliases for compatibility
    @property
    def player_wallet(self):
        return self.wallet_address

    @property
    def ap_earned(self):
        return self.ap_awarded

    @property
    def pool_name(self):
        return self.pool

    @property
    def event_time(self):
        return self.timestamp

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
        tier: Achievement tier (Bronze, Silver, Gold, Platinum, Diamond)
        ap_reward: AP rewarded when unlocked
        icon: Icon identifier/URL
        criteria: JSON string of unlock criteria
        category: Achievement category (mining, progression, etc.)
        created_at: When achievement was created
    """
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    tier = db.Column(db.String(20), nullable=False, default='Bronze')
    ap_reward = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(200), nullable=True)
    criteria = db.Column(db.Text, nullable=True)  # JSON string
    category = db.Column(db.String(50), nullable=True, default='general')
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


# ===================================
# DUNGEON EXPLORATION SYSTEM MODELS
# ===================================

class Dungeon(db.Model):
    """
    Dungeon model representing available dungeons to explore.

    Attributes:
        id: Auto-incrementing primary key
        name: Dungeon name
        description: Dungeon description/lore
        difficulty: Difficulty rating (1-5 stars)
        min_level_required: Minimum character level to enter
        ap_cost_per_run: AP cost to start a run
        max_floors: Maximum number of floors
        base_loot_multiplier: Multiplier for loot quality
        active: Whether dungeon is currently available
        unlock_requirements: JSON string of unlock conditions
        theme: Visual theme identifier
        created_at: When dungeon was added
    """
    __tablename__ = 'dungeons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=1)  # 1-5 stars
    min_level_required = db.Column(db.Integer, nullable=False, default=1)
    ap_cost_per_run = db.Column(db.Integer, nullable=False, default=50)
    max_floors = db.Column(db.Integer, nullable=False, default=10)
    base_loot_multiplier = db.Column(db.Float, nullable=False, default=1.0)
    active = db.Column(db.Boolean, default=True, nullable=False)
    unlock_requirements = db.Column(db.Text, nullable=True)  # JSON string
    theme = db.Column(db.String(50), nullable=True, default='dungeon')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    runs = db.relationship('DungeonRun', back_populates='dungeon', lazy='dynamic')
    monsters = db.relationship('Monster', back_populates='dungeon', lazy='dynamic')

    def __repr__(self):
        return f'<Dungeon {self.name} (Difficulty: {self.difficulty})>'

    def to_dict(self, include_stats=False):
        """Convert dungeon to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty,
            'min_level_required': self.min_level_required,
            'ap_cost_per_run': self.ap_cost_per_run,
            'max_floors': self.max_floors,
            'base_loot_multiplier': self.base_loot_multiplier,
            'active': self.active,
            'theme': self.theme,
        }

        if self.unlock_requirements:
            try:
                data['unlock_requirements'] = json.loads(self.unlock_requirements)
            except:
                data['unlock_requirements'] = {}

        if include_stats:
            total_runs = self.runs.count()
            completed_runs = self.runs.filter_by(status='completed').count()
            data['total_runs'] = total_runs
            data['completed_runs'] = completed_runs
            data['completion_rate'] = (completed_runs / total_runs * 100) if total_runs > 0 else 0

        return data


class DungeonRun(db.Model):
    """
    DungeonRun model representing a player's dungeon exploration session.

    Attributes:
        id: Auto-incrementing primary key
        player_id: Foreign key to Player
        dungeon_id: Foreign key to Dungeon
        current_floor: Current floor number
        furthest_floor_reached: Highest floor reached
        status: Run status (active/completed/abandoned/defeated)
        monsters_defeated: Total monsters defeated
        loot_collected: JSON array of loot items
        total_exp_gained: Total experience earned
        ap_spent: AP spent on this run
        current_room: Current room on floor
        player_health: Current player health
        unclaimed_loot: JSON array of unclaimed loot
        combat_state: JSON of current combat state
        started_at: When run started
        completed_at: When run ended
    """
    __tablename__ = 'dungeon_runs'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeons.id'), nullable=False)
    current_floor = db.Column(db.Integer, nullable=False, default=1)
    furthest_floor_reached = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default='active')  # active/completed/abandoned/defeated
    monsters_defeated = db.Column(db.Integer, nullable=False, default=0)
    loot_collected = db.Column(db.Text, nullable=True)  # JSON array
    total_exp_gained = db.Column(db.Integer, nullable=False, default=0)
    ap_spent = db.Column(db.Integer, nullable=False, default=0)
    current_room = db.Column(db.Integer, nullable=False, default=0)
    player_health = db.Column(db.Integer, nullable=True)
    unclaimed_loot = db.Column(db.Text, nullable=True)  # JSON array
    combat_state = db.Column(db.Text, nullable=True)  # JSON object
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    player = db.relationship('Player', back_populates='dungeon_runs')
    dungeon = db.relationship('Dungeon', back_populates='runs')

    def __repr__(self):
        return f'<DungeonRun {self.player_id} in {self.dungeon.name} - Floor {self.current_floor}>'

    def to_dict(self, include_dungeon=True):
        """Convert dungeon run to dictionary representation."""
        data = {
            'id': self.id,
            'player_id': self.player_id,
            'dungeon_id': self.dungeon_id,
            'current_floor': self.current_floor,
            'furthest_floor_reached': self.furthest_floor_reached,
            'status': self.status,
            'monsters_defeated': self.monsters_defeated,
            'total_exp_gained': self.total_exp_gained,
            'ap_spent': self.ap_spent,
            'current_room': self.current_room,
            'player_health': self.player_health,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

        if self.loot_collected:
            try:
                data['loot_collected'] = json.loads(self.loot_collected)
            except:
                data['loot_collected'] = []

        if self.unclaimed_loot:
            try:
                data['unclaimed_loot'] = json.loads(self.unclaimed_loot)
            except:
                data['unclaimed_loot'] = []

        if self.combat_state:
            try:
                data['combat_state'] = json.loads(self.combat_state)
            except:
                data['combat_state'] = None

        if include_dungeon:
            data['dungeon'] = self.dungeon.to_dict()

        return data


class PlayerCharacter(db.Model):
    """
    PlayerCharacter model representing RPG stats for a player.

    Attributes:
        player_id: Foreign key to Player (primary key)
        level: Current character level
        current_exp: Experience in current level
        total_exp: Lifetime total experience
        health: Current health
        max_health: Maximum health
        attack: Attack stat
        defense: Defense stat
        speed: Speed stat
        equipped_weapon_id: Foreign key to Gear
        equipped_armor_id: Foreign key to Gear
        stats_json: JSON string for future stat expansion
        created_at: Character creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = 'player_characters'

    player_id = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), primary_key=True)
    level = db.Column(db.Integer, nullable=False, default=1)
    current_exp = db.Column(db.Integer, nullable=False, default=0)
    total_exp = db.Column(db.Integer, nullable=False, default=0)
    health = db.Column(db.Integer, nullable=False, default=100)
    max_health = db.Column(db.Integer, nullable=False, default=100)
    attack = db.Column(db.Integer, nullable=False, default=10)
    defense = db.Column(db.Integer, nullable=False, default=5)
    speed = db.Column(db.Integer, nullable=False, default=10)
    equipped_weapon_id = db.Column(db.Integer, db.ForeignKey('gear.id'), nullable=True)
    equipped_armor_id = db.Column(db.Integer, db.ForeignKey('gear.id'), nullable=True)
    stats_json = db.Column(db.Text, nullable=True)  # JSON for future expansion
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='character')
    equipped_weapon = db.relationship('Gear', foreign_keys=[equipped_weapon_id])
    equipped_armor = db.relationship('Gear', foreign_keys=[equipped_armor_id])

    def __repr__(self):
        return f'<PlayerCharacter {self.player_id} Lv{self.level}>'

    @property
    def exp_to_next_level(self):
        """Calculate experience needed for next level."""
        return self.level * 100

    @property
    def total_attack(self):
        """Calculate total attack including equipment."""
        base = self.attack
        if self.equipped_weapon:
            weapon_stats = json.loads(self.equipped_weapon.stat_bonuses) if self.equipped_weapon.stat_bonuses else {}
            base += weapon_stats.get('attack', 0)
        return base

    @property
    def total_defense(self):
        """Calculate total defense including equipment."""
        base = self.defense
        if self.equipped_armor:
            armor_stats = json.loads(self.equipped_armor.stat_bonuses) if self.equipped_armor.stat_bonuses else {}
            base += armor_stats.get('defense', 0)
        return base

    def add_exp(self, exp_amount):
        """
        Add experience and handle level ups.

        Returns:
            int: Number of levels gained
        """
        self.current_exp += exp_amount
        self.total_exp += exp_amount

        levels_gained = 0
        while self.current_exp >= self.exp_to_next_level:
            self.current_exp -= self.exp_to_next_level
            self.level += 1
            levels_gained += 1

            # Stat increases per level
            self.max_health += 5
            self.health = self.max_health  # Full heal on level up
            self.attack += 2
            self.defense += 1

        return levels_gained

    def heal(self, amount):
        """Heal character by amount, not exceeding max health."""
        self.health = min(self.health + amount, self.max_health)

    def take_damage(self, amount):
        """Take damage, minimum 0 health."""
        self.health = max(0, self.health - amount)

    def to_dict(self, include_equipment=True):
        """Convert character to dictionary representation."""
        data = {
            'player_id': self.player_id,
            'level': self.level,
            'current_exp': self.current_exp,
            'total_exp': self.total_exp,
            'exp_to_next_level': self.exp_to_next_level,
            'health': self.health,
            'max_health': self.max_health,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'total_attack': self.total_attack,
            'total_defense': self.total_defense,
        }

        if include_equipment:
            if self.equipped_weapon:
                data['equipped_weapon'] = self.equipped_weapon.to_dict()
            else:
                data['equipped_weapon'] = None

            if self.equipped_armor:
                data['equipped_armor'] = self.equipped_armor.to_dict()
            else:
                data['equipped_armor'] = None

        return data


class Gear(db.Model):
    """
    Gear model representing equipment items.

    Attributes:
        id: Auto-incrementing primary key
        name: Gear name
        description: Gear description
        type: Gear type (weapon/armor/accessory)
        rarity: Rarity tier (common/uncommon/rare/epic/legendary)
        stat_bonuses: JSON object of stat bonuses
        level_requirement: Minimum level to use
        sell_value: AP value when sold
        sprite_url: Item sprite/icon URL
        special_effect: JSON description of special effects
        created_at: When gear was added
    """
    __tablename__ = 'gear'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), nullable=False)  # weapon/armor/accessory
    rarity = db.Column(db.String(20), nullable=False, default='common')  # common/uncommon/rare/epic/legendary
    stat_bonuses = db.Column(db.Text, nullable=True)  # JSON: {attack: 5, defense: 3}
    level_requirement = db.Column(db.Integer, nullable=False, default=1)
    sell_value = db.Column(db.Integer, nullable=False, default=10)
    sprite_url = db.Column(db.String(200), nullable=True)
    special_effect = db.Column(db.Text, nullable=True)  # JSON description
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    inventory_items = db.relationship('PlayerInventory', back_populates='gear', lazy='dynamic')

    def __repr__(self):
        return f'<Gear {self.name} ({self.rarity} {self.type})>'

    def to_dict(self):
        """Convert gear to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'rarity': self.rarity,
            'level_requirement': self.level_requirement,
            'sell_value': self.sell_value,
            'sprite_url': self.sprite_url,
        }

        if self.stat_bonuses:
            try:
                data['stat_bonuses'] = json.loads(self.stat_bonuses)
            except:
                data['stat_bonuses'] = {}

        if self.special_effect:
            try:
                data['special_effect'] = json.loads(self.special_effect)
            except:
                data['special_effect'] = None

        return data


class PlayerInventory(db.Model):
    """
    PlayerInventory model representing player's gear collection.

    Attributes:
        id: Auto-incrementing primary key
        player_id: Foreign key to Player
        gear_id: Foreign key to Gear
        quantity: Number of items (for stackable items)
        is_equipped: Whether item is currently equipped
        acquired_at: When item was acquired
    """
    __tablename__ = 'player_inventory'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(34), db.ForeignKey('players.wallet_address'), nullable=False)
    gear_id = db.Column(db.Integer, db.ForeignKey('gear.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_equipped = db.Column(db.Boolean, default=False, nullable=False)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship('Player', back_populates='inventory')
    gear = db.relationship('Gear', back_populates='inventory_items')

    def __repr__(self):
        return f'<PlayerInventory {self.player_id} - {self.gear.name} x{self.quantity}>'

    def to_dict(self, include_gear=True):
        """Convert inventory item to dictionary representation."""
        data = {
            'id': self.id,
            'player_id': self.player_id,
            'gear_id': self.gear_id,
            'quantity': self.quantity,
            'is_equipped': self.is_equipped,
            'acquired_at': self.acquired_at.isoformat() if self.acquired_at else None,
        }

        if include_gear:
            data['gear'] = self.gear.to_dict()

        return data


class Monster(db.Model):
    """
    Monster model representing enemy definitions.

    Attributes:
        id: Auto-incrementing primary key
        name: Monster name
        description: Monster description/lore
        dungeon_id: Foreign key to Dungeon (which dungeon this monster belongs to)
        dungeon_tier: Dungeon difficulty tier (1-5)
        level: Monster level
        health: Monster health points
        attack: Monster attack stat
        defense: Monster defense stat
        speed: Monster speed stat
        exp_reward: Experience points awarded
        loot_table: JSON array of possible loot
        sprite_url: Monster sprite/image URL
        special_abilities: JSON array of special abilities
        created_at: When monster was added
    """
    __tablename__ = 'monsters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    dungeon_id = db.Column(db.Integer, db.ForeignKey('dungeons.id'), nullable=False)
    dungeon_tier = db.Column(db.Integer, nullable=False, default=1)
    level = db.Column(db.Integer, nullable=False, default=1)
    health = db.Column(db.Integer, nullable=False, default=50)
    attack = db.Column(db.Integer, nullable=False, default=8)
    defense = db.Column(db.Integer, nullable=False, default=3)
    speed = db.Column(db.Integer, nullable=False, default=10)
    exp_reward = db.Column(db.Integer, nullable=False, default=20)
    loot_table = db.Column(db.Text, nullable=True)  # JSON array
    sprite_url = db.Column(db.String(200), nullable=True)
    special_abilities = db.Column(db.Text, nullable=True)  # JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dungeon = db.relationship('Dungeon', back_populates='monsters')

    def __repr__(self):
        return f'<Monster {self.name} Lv{self.level}>'

    def to_dict(self):
        """Convert monster to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dungeon_id': self.dungeon_id,
            'dungeon_tier': self.dungeon_tier,
            'level': self.level,
            'health': self.health,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'exp_reward': self.exp_reward,
            'sprite_url': self.sprite_url,
        }

        if self.loot_table:
            try:
                data['loot_table'] = json.loads(self.loot_table)
            except:
                data['loot_table'] = []

        if self.special_abilities:
            try:
                data['special_abilities'] = json.loads(self.special_abilities)
            except:
                data['special_abilities'] = []

        return data
