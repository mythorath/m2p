# M2P - Mining to Prosperity

A comprehensive leaderboard system for a mining/gaming application with real-time updates, caching, and achievements.

## 🌟 Features

### Leaderboard System
- **Multiple Ranking Periods:**
  - **All-Time:** Total mined ADVC across all time
  - **This Week:** Mining events from the last 7 days
  - **Today:** Mining events from the last 24 hours
  - **Efficiency:** ADVC per hour since registration

- **Performance Optimizations:**
  - Database caching with 5-minute refresh cycle
  - Redis caching for ultra-fast queries
  - Background tasks for automatic cache updates
  - Virtual scrolling for smooth performance with large datasets

- **Real-Time Updates:**
  - WebSocket connections for live rank changes
  - Automatic leaderboard refresh on updates
  - Rank change notifications

### Frontend Features
- **Leaderboard Component:**
  - Tabbed interface for different periods
  - Search by display name or wallet address
  - Filter by verified/unverified users
  - Player row highlighting
  - Rank change indicators (↑↓)
  - Virtual scrolling for performance

- **Widgets:**
  - **Podium Display:** Top 3 players with animated podium
  - **Rank Badge:** Show player's current rank with change indicators
  - **Progress Bar:** Track progress to next rank

### Achievement System
- **Leaderboard Achievements:**
  - Elite Miner (Top 10 All-Time)
  - Weekly Champion (Top 10 This Week)
  - Daily Dominator (Top 10 Today)
  - Legendary Miner (Top 100 All-Time)
  - Rising Star (Biggest Weekly Climber)
  - Efficiency Master (Top 10 Efficiency)
  - Podium Legend (Top 3 All-Time)
  - Number One (Rank #1 Any Period)

## 🏗️ Architecture

### Backend (FastAPI + SQLAlchemy)
```
backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration settings
├── database.py                # Database setup and session management
├── models/                    # SQLAlchemy models
│   ├── user.py               # User/Player model
│   ├── mining_event.py       # Mining event tracking
│   ├── leaderboard_cache.py  # Pre-computed rankings
│   └── achievement.py        # Achievement definitions
├── server/
│   ├── leaderboard.py        # LeaderboardManager class
│   ├── websocket.py          # WebSocket connection manager
│   ├── routes/
│   │   └── leaderboard.py    # Leaderboard API endpoints
│   └── tasks/
│       └── update_leaderboards.py  # Background scheduler
└── seed_achievements.py      # Seed initial achievement data
```

### Frontend (React + TypeScript + Vite)
```
frontend/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Main App component
│   ├── types/
│   │   └── leaderboard.ts    # TypeScript interfaces
│   ├── api/
│   │   └── leaderboard.ts    # API client
│   ├── hooks/
│   │   └── useWebSocket.ts   # WebSocket hook
│   └── components/
│       ├── Leaderboard.tsx   # Main leaderboard component
│       ├── PodiumWidget.tsx  # Top 3 podium display
│       ├── RankBadge.tsx     # Player rank badge
│       └── RankProgressBar.tsx  # Rank up progress
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Quick Start with Docker

1. **Clone the repository:**
```bash
git clone <repository-url>
cd m2p
```

2. **Start PostgreSQL and Redis:**
```bash
docker-compose up -d
```

3. **Set up the backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database and seed achievements
python -c "from database import init_db; init_db()"
python seed_achievements.py

# Start the backend server
python main.py
```

The backend will be available at `http://localhost:8000`

4. **Set up the frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Manual Database Setup

If not using Docker:

1. **Create PostgreSQL database:**
```bash
createdb m2p_db
createuser m2p_user
```

2. **Start Redis:**
```bash
redis-server
```

3. **Update `.env` file with your database credentials**

## 📡 API Endpoints

### Leaderboard Endpoints

#### Get Available Periods
```
GET /api/leaderboard/periods
```

#### Get Leaderboard
```
GET /api/leaderboard/{period}?limit=100&offset=0&use_cache=true
```

Parameters:
- `period`: `all_time` | `this_week` | `today` | `efficiency`
- `limit`: Number of entries (1-500, default: 100)
- `offset`: Pagination offset (default: 0)
- `use_cache`: Use cached data (default: true)

#### Get Player Rank
```
GET /api/leaderboard/{period}/player/{wallet_address}?context=5
```

Parameters:
- `period`: Leaderboard period
- `wallet_address`: Player's wallet address
- `context`: Number of nearby positions (0-20, default: 5)

#### Refresh Leaderboard
```
POST /api/leaderboard/{period}/refresh
```

#### Refresh All Leaderboards
```
POST /api/leaderboard/refresh-all
```

### WebSocket Endpoints

#### General Connection
```
ws://localhost:8000/ws
```

#### User-Specific Connection
```
ws://localhost:8000/ws/{wallet_address}
```

#### Events

**Rank Changed Event:**
```json
{
  "event": "rank_changed",
  "data": {
    "wallet_address": "0x...",
    "period": "all_time",
    "old_rank": 15,
    "new_rank": 12,
    "rank_change": -3,
    "direction": "up",
    "period_score": 1250.5,
    "timestamp": "2025-01-15T12:00:00Z"
  }
}
```

**Leaderboard Updated Event:**
```json
{
  "event": "leaderboard_updated",
  "data": {
    "period": "all_time",
    "timestamp": "2025-01-15T12:00:00Z"
  }
}
```

## 🔧 Configuration

### Backend Configuration (`.env`)

```env
# Database
DATABASE_URL=postgresql://m2p_user:m2p_password@localhost:5432/m2p_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key-here
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Leaderboard
LEADERBOARD_CACHE_TTL=300          # Cache TTL in seconds (5 minutes)
LEADERBOARD_UPDATE_INTERVAL=300    # Update interval in seconds (5 minutes)
LEADERBOARD_TOP_LIMIT=1000         # Maximum ranks to cache
```

### Frontend Configuration (`.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📊 Database Schema

### Tables

#### `users`
- Player information and mining statistics
- Fields: `id`, `wallet_address`, `display_name`, `is_verified`, `total_mined_advc`, `total_ap`, `created_at`, `last_mining_event`

#### `mining_events`
- Individual mining activities
- Fields: `id`, `user_id`, `advc_mined`, `ap_earned`, `event_type`, `timestamp`

#### `leaderboard_cache`
- Pre-computed rankings for fast queries
- Fields: `id`, `period`, `rank`, `previous_rank`, `user_id`, `wallet_address`, `display_name`, `is_verified`, `total_mined_advc`, `total_ap`, `period_score`, `last_mining_event`, `updated_at`

#### `achievements`
- Achievement definitions
- Fields: `id`, `code`, `name`, `description`, `category`, `requirement_type`, `requirement_value`, `ap_reward`, `icon`, `is_active`, `created_at`

#### `player_achievements`
- Earned achievements per player
- Fields: `id`, `user_id`, `achievement_id`, `earned_at`, `progress`, `extra_data`

## 🎯 Usage Examples

### Backend Usage

```python
from database import SessionLocal
from server.leaderboard import get_leaderboard_manager

# Get leaderboard manager
db = SessionLocal()
manager = get_leaderboard_manager(db)

# Get all-time rankings
rankings = manager.get_leaderboard('all_time', limit=100)

# Get player rank
rank_data = manager.get_player_rank('0x...', 'all_time', context=5)

# Update cache
update_counts = manager.update_leaderboard_cache()

# Handle mining event
rank_changes = manager.on_mining_event(user_id=123)
```

### Frontend Usage

```typescript
import { leaderboardAPI } from './api/leaderboard';
import { useWebSocket } from './hooks/useWebSocket';

// Fetch leaderboard
const data = await leaderboardAPI.getLeaderboard('all_time', 100, 0);

// Get player rank
const rank = await leaderboardAPI.getPlayerRank('all_time', '0x...', 5);

// WebSocket connection
const { isConnected, lastMessage } = useWebSocket({
  walletAddress: '0x...',
  onMessage: (message) => {
    if (message.event === 'rank_changed') {
      console.log('Your rank changed!', message.data);
    }
  },
});
```

## 🔄 Background Tasks

The system automatically updates leaderboard caches every 5 minutes using APScheduler.

**Manual trigger:**
```python
from server.tasks import update_all_leaderboards
update_all_leaderboards()
```

## 🎨 Customization

### Adding New Ranking Periods

1. Add period to `LeaderboardManager.PERIODS`
2. Implement calculation method
3. Update frontend types
4. Add tab to UI

### Adding New Achievements

```python
from models.achievement import Achievement
from database import SessionLocal

db = SessionLocal()
achievement = Achievement(
    code="new_achievement",
    name="New Achievement",
    description="Achievement description",
    category="leaderboard",
    requirement_type="rank",
    requirement_value='{"period": "all_time", "max_rank": 50}',
    ap_reward=500,
    icon="star"
)
db.add(achievement)
db.commit()
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.