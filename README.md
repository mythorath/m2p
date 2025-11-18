# M2P - Mine to Play Achievement System

A comprehensive achievement tracking and unlocking system for cryptocurrency mining gamification.

## 🎯 Features

- **26+ Achievements** across multiple categories
- **Real-time WebSocket notifications** for instant achievement unlocks
- **Beautiful animated popup** with particle effects and sound
- **Progress tracking** for all achievements
- **Achievement Points (AP)** reward system
- **Leaderboard rankings**
- **Daily statistics** and streak tracking

## 📁 Project Structure

```
m2p/
├── server/                      # Backend (Python/Flask)
│   ├── models.py               # Database models
│   ├── achievements.py         # Achievement manager
│   ├── achievements_data.py    # Achievement definitions (26 achievements)
│   ├── pool_poller.py          # Mining pool integration
│   ├── seed_achievements.py    # Database seeding script
│   ├── database.py             # Database configuration
│   └── app.py                  # Flask server with WebSocket
├── client/                      # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── AchievementUnlockPopup.jsx
│   │   │   └── AchievementUnlockPopup.css
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   │   └── index.html
│   └── package.json
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🚀 Quick Start

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database:**
   ```bash
   python server/database.py
   ```

3. **Seed achievements:**
   ```bash
   python server/seed_achievements.py
   ```

4. **Start the Flask server:**
   ```bash
   python server/app.py
   ```
   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Install Node dependencies:**
   ```bash
   cd client
   npm install
   ```

2. **Start the React development server:**
   ```bash
   npm start
   ```
   Frontend will run on `http://localhost:3000`

## 🎮 Achievement Categories

### Mining Milestones (6 achievements)
- Genesis Miner - First mining reward
- Double Digits - Mine 10 ADVC
- Century Mark - Mine 100 ADVC
- Millennium Miner - Mine 1,000 ADVC
- Mining Whale - Mine 10,000 ADVC
- Legendary Miner - Mine 100,000 ADVC (hidden)

### Streak Achievements (4 achievements)
- Daily Habit - 3 consecutive days
- Marathon Miner - 7 consecutive days
- Committed Miner - 30 consecutive days
- Unstoppable Force - 100 consecutive days (hidden)

### Daily Performance (4 achievements)
- Productive Day - Mine 5 ADVC in one day
- Speed Demon - Mine 10 ADVC in one day
- Power Miner - Mine 50 ADVC in one day
- Daily Legend - Mine 100 ADVC in one day (hidden)

### Pool Diversity (4 achievements)
- Pool Explorer - Mine on 2 pools
- Pool Hopper - Mine on 3 pools
- Pool Nomad - Mine on 5 pools
- Pool Master - Mine on 10 pools

### Mining Events (4 achievements)
- Active Miner - 10 mining events
- Dedicated Miner - 100 mining events
- Veteran Miner - 1,000 mining events
- Eternal Miner - 10,000 mining events (hidden)

### Leaderboard (4 achievements)
- Rising Star - Top 100
- Elite Miner - Top 50
- Top Ten - Top 10
- Champion - #1 (hidden)

## 🔌 API Endpoints

### Players
- `POST /api/players` - Create a new player
- `GET /api/players/<id>` - Get player information
- `GET /api/players/<id>/achievements` - Get player achievements
- `POST /api/players/<id>/achievements/check` - Manually check achievements
- `GET /api/players/<id>/mining-stats` - Get mining statistics

### Achievements
- `GET /api/achievements` - Get all achievements

### Mining
- `POST /api/mining/reward` - Process a mining reward
  ```json
  {
    "player_id": 1,
    "amount": 0.001,
    "pool_id": "pool_1",
    "pool_name": "MainPool"
  }
  ```

### Leaderboard
- `GET /api/leaderboard?category=total_mined&limit=100` - Get leaderboard

### Admin
- `POST /api/admin/award-achievement` - Manually award achievement

## 🎨 Frontend Components

### AchievementUnlockPopup
Beautiful animated popup with:
- Gradient background
- Icon with particle effects
- Animated entrance/exit
- Sound effects
- AP reward display
- Category badge
- Auto-dismiss (5 seconds)

### useWebSocket Hook
React hook for WebSocket management:
```javascript
const {
  isConnected,
  achievementNotification,
  clearAchievementNotification,
  emit
} = useWebSocket(playerId);
```

## 📊 Database Models

### Player
- User information and stats
- Total mined, AP, streaks
- Mining history tracking

### Achievement
- Achievement definitions
- Condition types and values
- AP rewards

### PlayerAchievement
- Player-achievement junction
- Progress tracking (0.0 - 1.0)
- Unlock timestamps

### MiningEvent
- Individual mining events
- Amount and pool tracking
- Timestamp records

### DailyMiningStats
- Daily aggregated statistics
- Event counts
- Unique pool tracking

## 🔔 WebSocket Events

### Client to Server
- `authenticate` - Authenticate with player ID

### Server to Client
- `notification` - Achievement unlocks and mining rewards
- `broadcast` - Global announcements

## 🧪 Testing

### Test Mining Reward
```bash
curl -X POST http://localhost:5000/api/mining/reward \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": 1,
    "amount": 0.001,
    "pool_id": "pool_1",
    "pool_name": "MainPool"
  }'
```

### Create Test Player
```bash
curl -X POST http://localhost:5000/api/players \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "wallet_address": "0x1234567890abcdef"
  }'
```

## 🎯 Achievement System Flow

1. **Mining Event Occurs**
   - Player earns mining reward from pool

2. **Process Reward**
   - `PoolPoller.process_mining_reward()` called
   - Updates player stats
   - Creates mining event record
   - Updates daily stats
   - Updates consecutive days streak

3. **Check Achievements**
   - `AchievementManager.check_achievements()` called
   - Each achievement condition evaluated
   - Progress calculated
   - Newly unlocked achievements identified

4. **Award & Notify**
   - AP awarded to player
   - Achievement record created/updated
   - WebSocket notification sent
   - Frontend displays popup

## 🛠️ Development

### Add New Achievement
1. Add to `server/achievements_data.py`
2. Run seeding script: `python server/seed_achievements.py`
3. Achievement automatically available!

### Add New Condition Type
1. Add condition checker method in `AchievementManager`
2. Add to `_check_condition()` handlers dict
3. Use in achievement definitions

## 📝 Environment Variables

See `.env.example` for configuration options:
- Database URL
- Server settings
- Frontend API URL
- Pool polling interval

## 🔒 Production Considerations

- Change `SECRET_KEY` in production
- Use PostgreSQL instead of SQLite
- Set up proper authentication
- Implement rate limiting
- Add API key protection
- Enable HTTPS
- Configure CORS properly

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please submit issues and pull requests.

## 🎉 Credits

Built for the M2P (Mine to Play) platform to gamify cryptocurrency mining with achievements and rewards!
