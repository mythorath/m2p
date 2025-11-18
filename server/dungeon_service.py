"""
Dungeon Service for M2P Game System.

This module handles all game logic for the dungeon exploration system including:
- Combat calculations (damage, turn order, victory conditions)
- Loot generation (rarity rolls, stat generation)
- Progression calculations (experience, level ups)
- Dungeon encounter generation (monster selection, room types)
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from models import (
    db, Dungeon, DungeonRun, PlayerCharacter, Gear,
    PlayerInventory, Monster, Player
)


class DungeonService:
    """Service class for dungeon exploration game logic."""

    # Loot rarity probabilities
    LOOT_RARITIES = {
        'common': {'chance': 0.60, 'stat_min': 1, 'stat_max': 5, 'value': 10},
        'uncommon': {'chance': 0.25, 'stat_min': 5, 'stat_max': 10, 'value': 25},
        'rare': {'chance': 0.10, 'stat_min': 10, 'stat_max': 20, 'value': 50},
        'epic': {'chance': 0.04, 'stat_min': 20, 'stat_max': 35, 'value': 100},
        'legendary': {'chance': 0.01, 'stat_min': 35, 'stat_max': 50, 'value': 250},
    }

    # Room encounter types
    ROOM_TYPES = {
        'monster': 0.70,  # 70% chance for monster battle
        'treasure': 0.20,  # 20% chance for treasure room
        'rest': 0.10,      # 10% chance for rest area
    }

    def __init__(self, app=None, socketio=None):
        """
        Initialize dungeon service.

        Args:
            app: Flask application instance
            socketio: SocketIO instance for real-time updates
        """
        self.app = app
        self.socketio = socketio

    # ==========================================
    # COMBAT SYSTEM
    # ==========================================

    def calculate_damage(self, attacker_attack: int, defender_defense: int) -> int:
        """
        Calculate damage dealt in combat.

        Formula: (Attack - Defense) * random(0.8-1.2)
        Minimum damage: 1

        Args:
            attacker_attack: Attacker's attack stat
            defender_defense: Defender's defense stat

        Returns:
            int: Damage amount (minimum 1)
        """
        base_damage = max(1, attacker_attack - defender_defense)
        damage_multiplier = random.uniform(0.8, 1.2)
        final_damage = int(base_damage * damage_multiplier)
        return max(1, final_damage)

    def execute_combat_turn(
        self,
        run: DungeonRun,
        action: str = 'attack'
    ) -> Dict:
        """
        Execute a single combat turn.

        Args:
            run: Active dungeon run
            action: Player action ('attack', 'defend', 'flee')

        Returns:
            Dict: Combat result with damage dealt, status updates
        """
        if not run.combat_state:
            return {'success': False, 'message': 'No active combat'}

        combat = json.loads(run.combat_state)
        character = run.player.character
        monster = Monster.query.get(combat['monster_id'])

        if not character or not monster:
            return {'success': False, 'message': 'Invalid combat state'}

        result = {
            'success': True,
            'action': action,
            'player_damage_dealt': 0,
            'monster_damage_dealt': 0,
            'player_health': character.health,
            'monster_health': combat['monster_health'],
            'combat_ended': False,
            'victory': False,
            'rewards': None,
        }

        # Player action
        if action == 'attack':
            damage = self.calculate_damage(character.total_attack, monster.defense)
            combat['monster_health'] -= damage
            result['player_damage_dealt'] = damage

        elif action == 'defend':
            # Defending reduces incoming damage by 50%
            result['defending'] = True

        elif action == 'flee':
            # 60% chance to escape
            if random.random() < 0.6:
                run.combat_state = None
                db.session.commit()
                return {
                    'success': True,
                    'action': 'flee',
                    'fled': True,
                    'combat_ended': True,
                }
            else:
                result['flee_failed'] = True

        # Check if monster defeated
        if combat['monster_health'] <= 0:
            result['combat_ended'] = True
            result['victory'] = True
            result['rewards'] = self._process_monster_defeat(run, monster)
            run.combat_state = None
            run.monsters_defeated += 1
            db.session.commit()
            return result

        # Monster turn (if not defeated)
        monster_damage = self.calculate_damage(monster.attack, character.total_defense)

        if result.get('defending'):
            monster_damage = int(monster_damage * 0.5)

        character.take_damage(monster_damage)
        result['monster_damage_dealt'] = monster_damage
        result['player_health'] = character.health

        # Check if player defeated
        if character.health <= 0:
            result['combat_ended'] = True
            result['victory'] = False
            result['player_defeated'] = True
            self._process_player_defeat(run)
            db.session.commit()
            return result

        # Update combat state
        combat['monster_health'] = max(0, combat['monster_health'])
        combat['turn_count'] = combat.get('turn_count', 0) + 1
        run.combat_state = json.dumps(combat)
        run.player_health = character.health

        db.session.commit()
        return result

    def _process_monster_defeat(self, run: DungeonRun, monster: Monster) -> Dict:
        """
        Process rewards when monster is defeated.

        Args:
            run: Active dungeon run
            monster: Defeated monster

        Returns:
            Dict: Rewards (exp, loot)
        """
        character = run.player.character

        # Award experience
        exp_gained = monster.exp_reward
        levels_gained = character.add_exp(exp_gained)
        run.total_exp_gained += exp_gained

        rewards = {
            'exp': exp_gained,
            'levels_gained': levels_gained,
            'loot': [],
        }

        # Roll for loot
        if monster.loot_table:
            try:
                loot_table = json.loads(monster.loot_table)
                for loot_entry in loot_table:
                    if random.random() < loot_entry.get('drop_chance', 0.5):
                        loot_item = self.generate_loot(
                            run.dungeon.base_loot_multiplier,
                            character.level
                        )
                        rewards['loot'].append(loot_item)

                        # Add to unclaimed loot
                        unclaimed = json.loads(run.unclaimed_loot) if run.unclaimed_loot else []
                        unclaimed.append(loot_item)
                        run.unclaimed_loot = json.dumps(unclaimed)
            except:
                pass

        return rewards

    def _process_player_defeat(self, run: DungeonRun):
        """
        Process player defeat in dungeon.

        Player loses all unclaimed loot but keeps earned experience.
        """
        run.status = 'defeated'
        run.unclaimed_loot = json.dumps([])  # Lose unclaimed loot
        run.completed_at = datetime.utcnow()

    # ==========================================
    # LOOT GENERATION
    # ==========================================

    def generate_loot(
        self,
        loot_multiplier: float = 1.0,
        player_level: int = 1
    ) -> Dict:
        """
        Generate random loot item.

        Args:
            loot_multiplier: Dungeon loot quality multiplier
            player_level: Player's character level

        Returns:
            Dict: Generated loot item data
        """
        # Roll for rarity
        rarity = self._roll_rarity(loot_multiplier)
        rarity_data = self.LOOT_RARITIES[rarity]

        # Determine gear type
        gear_type = random.choice(['weapon', 'armor'])

        # Generate stats
        if gear_type == 'weapon':
            attack_bonus = random.randint(rarity_data['stat_min'], rarity_data['stat_max'])
            stat_bonuses = {'attack': attack_bonus}
        else:  # armor
            defense_bonus = random.randint(rarity_data['stat_min'], rarity_data['stat_max'])
            health_bonus = random.randint(rarity_data['stat_min'] * 2, rarity_data['stat_max'] * 2)
            stat_bonuses = {'defense': defense_bonus, 'max_health': health_bonus}

        # Generate name
        name = self._generate_gear_name(gear_type, rarity)

        # Level requirement (based on stats)
        level_req = max(1, (rarity_data['stat_max'] // 10) * 2)

        loot_item = {
            'name': name,
            'type': gear_type,
            'rarity': rarity,
            'stat_bonuses': stat_bonuses,
            'level_requirement': level_req,
            'sell_value': rarity_data['value'],
            'description': f'A {rarity} {gear_type} found in the dungeon.',
        }

        return loot_item

    def _roll_rarity(self, multiplier: float = 1.0) -> str:
        """
        Roll for loot rarity based on probabilities.

        Args:
            multiplier: Multiplier to adjust rare drop chances

        Returns:
            str: Rarity tier
        """
        roll = random.random()

        # Adjust probabilities with multiplier (increases rare drops)
        cumulative = 0.0
        adjusted_rarities = []

        for rarity, data in self.LOOT_RARITIES.items():
            chance = data['chance']
            # Apply multiplier more heavily to rare items
            if rarity in ['epic', 'legendary']:
                chance *= multiplier
            adjusted_rarities.append((rarity, chance))

        # Normalize probabilities
        total = sum(c for _, c in adjusted_rarities)
        adjusted_rarities = [(r, c/total) for r, c in adjusted_rarities]

        # Roll with adjusted probabilities
        for rarity, chance in adjusted_rarities:
            cumulative += chance
            if roll <= cumulative:
                return rarity

        return 'common'

    def _generate_gear_name(self, gear_type: str, rarity: str) -> str:
        """Generate a random gear name based on type and rarity."""

        weapon_prefixes = {
            'common': ['Rusty', 'Old', 'Simple', 'Basic'],
            'uncommon': ['Sharp', 'Sturdy', 'Fine', 'Quality'],
            'rare': ['Enhanced', 'Superior', 'Reinforced', 'Tempered'],
            'epic': ['Master', 'Elite', 'Exquisite', 'Legendary'],
            'legendary': ['Mythical', 'Divine', 'Ancient', 'Ethereal'],
        }

        armor_prefixes = {
            'common': ['Worn', 'Tattered', 'Simple', 'Basic'],
            'uncommon': ['Sturdy', 'Solid', 'Reliable', 'Quality'],
            'rare': ['Reinforced', 'Hardened', 'Superior', 'Enhanced'],
            'epic': ['Master-crafted', 'Elite', 'Fortified', 'Legendary'],
            'legendary': ['Mythical', 'Divine', 'Ancient', 'Ethereal'],
        }

        weapon_types = ['Sword', 'Axe', 'Mace', 'Dagger', 'Spear', 'Hammer']
        armor_types = ['Chestplate', 'Helmet', 'Gauntlets', 'Boots', 'Shield']

        if gear_type == 'weapon':
            prefix = random.choice(weapon_prefixes[rarity])
            base = random.choice(weapon_types)
        else:
            prefix = random.choice(armor_prefixes[rarity])
            base = random.choice(armor_types)

        return f"{prefix} {base}"

    def create_gear_from_loot(self, loot_data: Dict) -> Gear:
        """
        Create a Gear database entry from loot data.

        Args:
            loot_data: Loot item dictionary

        Returns:
            Gear: Created gear instance
        """
        gear = Gear(
            name=loot_data['name'],
            description=loot_data.get('description', ''),
            type=loot_data['type'],
            rarity=loot_data['rarity'],
            stat_bonuses=json.dumps(loot_data['stat_bonuses']),
            level_requirement=loot_data['level_requirement'],
            sell_value=loot_data['sell_value'],
        )
        db.session.add(gear)
        db.session.flush()  # Get the ID without committing
        return gear

    # ==========================================
    # DUNGEON EXPLORATION
    # ==========================================

    def generate_room_encounter(
        self,
        dungeon: Dungeon,
        floor: int
    ) -> Dict:
        """
        Generate a room encounter for the current floor.

        Args:
            dungeon: Dungeon being explored
            floor: Current floor number

        Returns:
            Dict: Encounter data (type, monster, rewards)
        """
        # Roll for room type
        roll = random.random()
        cumulative = 0.0
        room_type = 'monster'

        for rtype, chance in self.ROOM_TYPES.items():
            cumulative += chance
            if roll <= cumulative:
                room_type = rtype
                break

        encounter = {
            'type': room_type,
            'floor': floor,
        }

        if room_type == 'monster':
            # Select random monster from dungeon
            monsters = dungeon.monsters.filter(
                Monster.level <= floor * 2 + dungeon.difficulty
            ).all()

            if monsters:
                monster = random.choice(monsters)
                encounter['monster'] = monster.to_dict()
                encounter['monster_id'] = monster.id
            else:
                # Fallback to treasure room if no monsters
                encounter['type'] = 'treasure'

        elif room_type == 'treasure':
            # Generate loot chest
            loot_count = random.randint(1, 3)
            encounter['loot_count'] = loot_count

        elif room_type == 'rest':
            # Rest area heals player
            encounter['heal_percent'] = 0.30  # Heal 30% HP

        return encounter

    def start_combat(
        self,
        run: DungeonRun,
        monster: Monster
    ) -> Dict:
        """
        Initialize combat with a monster.

        Args:
            run: Active dungeon run
            monster: Monster to fight

        Returns:
            Dict: Initial combat state
        """
        combat_state = {
            'monster_id': monster.id,
            'monster_health': monster.health,
            'turn_count': 0,
            'started_at': datetime.utcnow().isoformat(),
        }

        run.combat_state = json.dumps(combat_state)
        run.player_health = run.player.character.health
        db.session.commit()

        return {
            'success': True,
            'combat_state': combat_state,
            'monster': monster.to_dict(),
            'player_stats': run.player.character.to_dict(),
        }

    def advance_floor(self, run: DungeonRun) -> Dict:
        """
        Advance to the next floor in the dungeon.

        Args:
            run: Active dungeon run

        Returns:
            Dict: Result of advancement
        """
        if run.current_floor >= run.dungeon.max_floors:
            return {
                'success': False,
                'message': 'Already at maximum floor',
            }

        run.current_floor += 1
        run.current_room = 0

        if run.current_floor > run.furthest_floor_reached:
            run.furthest_floor_reached = run.current_floor

        db.session.commit()

        return {
            'success': True,
            'current_floor': run.current_floor,
            'message': f'Advanced to floor {run.current_floor}',
        }

    def claim_loot(self, run: DungeonRun, player_id: str) -> List[Gear]:
        """
        Claim all unclaimed loot and add to player inventory.

        Args:
            run: Dungeon run
            player_id: Player wallet address

        Returns:
            List[Gear]: List of claimed gear
        """
        if not run.unclaimed_loot:
            return []

        try:
            unclaimed = json.loads(run.unclaimed_loot)
        except:
            return []

        claimed_gear = []

        for loot_data in unclaimed:
            # Create gear instance
            gear = self.create_gear_from_loot(loot_data)

            # Add to player inventory
            inventory_item = PlayerInventory(
                player_id=player_id,
                gear_id=gear.id,
                quantity=1,
            )
            db.session.add(inventory_item)
            claimed_gear.append(gear)

            # Add to loot_collected
            collected = json.loads(run.loot_collected) if run.loot_collected else []
            collected.append(loot_data)
            run.loot_collected = json.dumps(collected)

        # Clear unclaimed loot
        run.unclaimed_loot = json.dumps([])
        db.session.commit()

        return claimed_gear

    def complete_dungeon_run(self, run: DungeonRun) -> Dict:
        """
        Complete a dungeon run successfully.

        Args:
            run: Dungeon run to complete

        Returns:
            Dict: Completion summary
        """
        run.status = 'completed'
        run.completed_at = datetime.utcnow()

        # Claim any unclaimed loot
        claimed_gear = self.claim_loot(run, run.player_id)

        db.session.commit()

        return {
            'success': True,
            'status': 'completed',
            'floors_cleared': run.furthest_floor_reached,
            'monsters_defeated': run.monsters_defeated,
            'exp_gained': run.total_exp_gained,
            'loot_claimed': len(claimed_gear),
        }

    def abandon_dungeon_run(self, run: DungeonRun) -> Dict:
        """
        Abandon a dungeon run (lose unclaimed loot).

        Args:
            run: Dungeon run to abandon

        Returns:
            Dict: Abandonment result
        """
        run.status = 'abandoned'
        run.completed_at = datetime.utcnow()

        # Keep experience but lose unclaimed loot
        run.unclaimed_loot = json.dumps([])

        db.session.commit()

        return {
            'success': True,
            'status': 'abandoned',
            'exp_kept': run.total_exp_gained,
            'loot_lost': True,
        }

    # ==========================================
    # CHARACTER MANAGEMENT
    # ==========================================

    def create_character(self, player_id: str) -> PlayerCharacter:
        """
        Create a new character for a player.

        Args:
            player_id: Player wallet address

        Returns:
            PlayerCharacter: Created character
        """
        character = PlayerCharacter(player_id=player_id)
        db.session.add(character)
        db.session.commit()
        return character

    def equip_gear(
        self,
        character: PlayerCharacter,
        inventory_item: PlayerInventory
    ) -> Dict:
        """
        Equip gear from inventory.

        Args:
            character: Player character
            inventory_item: Inventory item to equip

        Returns:
            Dict: Equip result
        """
        gear = inventory_item.gear

        # Check level requirement
        if character.level < gear.level_requirement:
            return {
                'success': False,
                'message': f'Requires level {gear.level_requirement}',
            }

        # Unequip existing gear of same type
        if gear.type == 'weapon':
            if character.equipped_weapon_id:
                old_inv = PlayerInventory.query.filter_by(
                    player_id=character.player_id,
                    gear_id=character.equipped_weapon_id,
                    is_equipped=True
                ).first()
                if old_inv:
                    old_inv.is_equipped = False
            character.equipped_weapon_id = gear.id

        elif gear.type == 'armor':
            if character.equipped_armor_id:
                old_inv = PlayerInventory.query.filter_by(
                    player_id=character.player_id,
                    gear_id=character.equipped_armor_id,
                    is_equipped=True
                ).first()
                if old_inv:
                    old_inv.is_equipped = False
            character.equipped_armor_id = gear.id

        inventory_item.is_equipped = True
        db.session.commit()

        return {
            'success': True,
            'equipped': gear.to_dict(),
            'new_stats': character.to_dict(),
        }

    def sell_gear(
        self,
        player: Player,
        inventory_item: PlayerInventory
    ) -> Dict:
        """
        Sell gear for AP.

        Args:
            player: Player
            inventory_item: Inventory item to sell

        Returns:
            Dict: Sale result
        """
        gear = inventory_item.gear

        # Can't sell equipped gear
        if inventory_item.is_equipped:
            return {
                'success': False,
                'message': 'Cannot sell equipped gear',
            }

        # Award AP
        player.total_ap += gear.sell_value

        # Remove from inventory
        db.session.delete(inventory_item)
        db.session.commit()

        return {
            'success': True,
            'ap_gained': gear.sell_value,
            'new_ap_balance': player.available_ap,
        }

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def get_dungeon_leaderboard(
        self,
        dungeon_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top performers for a specific dungeon.

        Args:
            dungeon_id: Dungeon ID
            limit: Number of results

        Returns:
            List[Dict]: Leaderboard entries
        """
        top_runs = DungeonRun.query.filter_by(
            dungeon_id=dungeon_id,
            status='completed'
        ).order_by(
            DungeonRun.furthest_floor_reached.desc(),
            DungeonRun.monsters_defeated.desc()
        ).limit(limit).all()

        leaderboard = []
        for idx, run in enumerate(top_runs, 1):
            leaderboard.append({
                'rank': idx,
                'player_id': run.player_id,
                'display_name': run.player.display_name,
                'floors_cleared': run.furthest_floor_reached,
                'monsters_defeated': run.monsters_defeated,
                'completed_at': run.completed_at.isoformat() if run.completed_at else None,
            })

        return leaderboard
