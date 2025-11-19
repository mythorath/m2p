# M2P (Mine to Play) - AI Coding Agent Instructions

## Project Overview

M2P is a cryptocurrency mining rewards platform integrated with a dungeon crawler RPG. Players earn Action Points (AP) from mining ADVC (Advancecoin) and spend them in turn-based dungeon combat. The system combines blockchain wallet verification, real-time WebSocket updates, and complex game mechanics.

**Core Architecture:**
- **Backend:** Flask + Flask-SocketIO + SQLAlchemy (Python 3.9+)
- **Frontend:** React 18 with Context API and WebSocket client
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Real-time:** WebSocket for combat events, achievements, mining rewards

## Critical Database Schema

The system uses **11 interconnected tables**. Key relationships:
- `Player` (wallet_address PK) → `PlayerCharacter` (1:1), `DungeonRun` (1:many), `PlayerInventory` (1:many)
- `DungeonRun` links Player, Dungeon, and current Monster encounter
- `PlayerInventory` stores equipped and unequipped Gear items

**Wallet format:** Advancecoin addresses start with 'A' and are exactly 34 characters (`^A[a-zA-Z0-9]{33}$`)

See `server/models.py` for complete schema with relationships and helper methods.

## Essential Workflows

### Development Setup
```bash
# Backend
cd server && python -c "from app import app, db; app.app_context().push(); db.create_all()"
python seed_dungeons.py && python seed_dungeon_achievements.py
python app.py  # Runs on port 5000

# Frontend
cd client && npm install && npm start  # Runs on port 3000
```

### Testing
```bash
make test              # All tests via pytest
make test-unit         # Unit tests only
make test-integration  # Integration tests
make test-cov          # With coverage report
```

Tests use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.db`, `@pytest.mark.api` (see `pytest.ini`)

### Database Operations
```bash
# Reset database (DESTRUCTIVE)
rm server/m2p.db && cd server && python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Seed game data (dungeons, monsters, gear, achievements)
python server/seed_dungeons.py
python server/seed_dungeon_achievements.py
```

## Key Architectural Patterns

### Service Layer Architecture
Business logic lives in service classes, **not** in Flask routes:
- `DungeonService` (server/dungeon_service.py) - Combat calculations, loot generation, XP progression
- `AchievementService` (server/achievement_service.py) - Achievement checking with criteria evaluation

Example: Combat damage uses `DungeonService.calculate_damage(attack, defense)` which applies variance formula: `(Attack - Defense) * random(0.8-1.2)`

### WebSocket Communication Pattern
Real-time events broadcast via `socketio.emit()` for global events:
```python
socketio.emit('achievement_unlocked', {
    'wallet': player.wallet_address,
    'achievement': achievement.to_dict(),
    'reward_ap': achievement.reward_ap
}, room=player.wallet_address)
```

Players join rooms by wallet address. Client subscribes in `useWebSocket.js` hook.

### API Response Structure
All API endpoints return consistent JSON:
```python
# Success
return jsonify({'success': True, 'data': {...}}), 200

# Error
return jsonify({'error': 'Description of error'}), 400
```

Frontend expects `.data` or `.error` properties (see `client/src/services/api.js`).

### Loot Rarity System
Defined in `DungeonService.LOOT_RARITIES` with weighted probabilities:
- Common (60%), Uncommon (25%), Rare (10%), Epic (4%), Legendary (1%)
- Each rarity has `stat_min`, `stat_max`, and `value` for gold pricing

## Critical Developer Knowledge

### Player Verification Flow
1. Register → Returns `challenge_amount` (unique decimal)
2. Player sends exact ADVC amount to donation address
3. Backend polls blockchain API, verifies transaction
4. Sets `player.verified = True` → Unlocks full features

Verification expires after 24 hours (`challenge_expires_at`).

### AP Economy
- Mining rewards → `total_ap` increases
- Dungeon entry costs AP → `spent_ap` increases
- Available AP = `total_ap - spent_ap` (computed property on Player model)

**Important:** Always use `player.available_ap` property, never manually calculate.

### Combat Turn System
State machine in `DungeonRun.state`:
- `exploring` → Player can move to next floor
- `in_combat` → Player must attack/defend/flee
- `completed` → Dungeon finished, rewards given
- `abandoned` → Player fled or died

See `dungeon_service.py:execute_combat_turn()` for full turn logic.

### Equipment System
`Gear` has `slot` field: 'weapon', 'armor', 'accessory'
Players can equip ONE item per slot via `PlayerInventory.equipped` boolean.
Stats stack additively across all equipped gear.

## Common Pitfalls

1. **Don't query database outside Flask app context** - Always wrap in `with app.app_context():`
2. **Achievement criteria is JSON string** - Parse with `json.loads(achievement.criteria)` before evaluation
3. **WebSocket events need room context** - Emit to `room=wallet_address`, not globally
4. **Frontend uses React Context for player state** - Access via `useContext(GameContext)`, don't duplicate state
5. **SQLAlchemy relationships are lazy by default** - Use `joinedload()` or switch to `lazy='dynamic'` for collections

## File Navigation

**Key entry points:**
- `server/app.py` - Flask routes and WebSocket handlers (1785 lines)
- `server/dungeon_service.py` - Game logic and combat math (741 lines)
- `client/src/components/DungeonView.js` - Main game UI (536 lines)
- `server/models.py` - Complete database schema (796 lines)

**Testing:**
- `server/tests/conftest.py` - Pytest fixtures (274 lines)
- `server/tests/test_*.py` - Test files with markers

**Documentation:**
- `docs/ARCHITECTURE.md` - Full system design
- `API_DOCUMENTATION.md` - Complete REST API reference
- `SETUP_AND_TEST_GUIDE.md` - Complete testing checklist (100+ items)

## Project Conventions

- Python: PEP 8, 4-space indent, snake_case
- JavaScript: camelCase, 2-space indent
- Database: snake_case table/column names
- API routes: `/api/<resource>/<action>` pattern
- Components: PascalCase files, one component per file
- Services: Singleton pattern with app and socketio injection
