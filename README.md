# Mine-to-Play (M2P)

A gamified platform that rewards cryptocurrency miners with Achievement Points (AP) for mining ADVC (AdvCash). Players earn AP based on their mining activity across multiple pools and can unlock achievements, compete on leaderboards, and redeem rewards.

## Project Overview

Mine-to-Play bridges cryptocurrency mining with gaming mechanics by:
- Tracking mining activity across multiple ADVC pools (cpu-pool.com, rplant.xyz, zpool.ca)
- Awarding Achievement Points (AP) based on ADVC mined (1 ADVC = 100 AP)
- Providing achievements for milestones and consistency
- Enabling wallet verification through on-chain transactions
- Offering leaderboards and competitive rankings

## Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-SocketIO** - Real-time WebSocket communication
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Flask-Migrate** - Database migrations
- **aiohttp** - Async HTTP client for pool APIs
- **BeautifulSoup4** - HTML parsing

### Frontend (To be implemented)
- **React** - UI framework
- **Vite** - Build tool
- **Socket.IO Client** - Real-time updates

## Project Structure

```
m2p/
├── server/                 # Backend Flask application
│   ├── __init__.py        # Application factory
│   ├── models.py          # SQLAlchemy models
│   ├── config.py          # Configuration classes
│   ├── init_db.py         # Database initialization script
│   └── requirements.txt   # Python dependencies
├── client/                 # Frontend React application (TBD)
├── docs/                   # Documentation
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Database Schema

### Player
Represents a player/miner in the system.
- `id`: Primary key
- `wallet_address`: Unique ADVC wallet address (64 chars)
- `display_name`: Optional display name
- `verified`: Wallet verification status
- `verification_amount`: Amount sent for verification
- `verification_tx_hash`: Transaction hash of verification
- `total_ap`: Total Achievement Points earned
- `spent_ap`: AP spent on rewards
- `total_mined_advc`: Total ADVC mined across all pools
- `created_at`: Account creation timestamp
- `last_seen_at`: Last activity timestamp

### MiningEvent
Records individual mining payouts from pools.
- `id`: Primary key
- `player_id`: Foreign key to Player
- `pool_name`: Name of mining pool
- `amount_advc`: Amount of ADVC in this payout
- `ap_awarded`: AP awarded for this event
- `detected_at`: When payout was detected

### PoolSnapshot
Periodic snapshots of cumulative pool payouts.
- `id`: Primary key
- `player_id`: Foreign key to Player
- `pool_name`: Pool identifier
- `paid_amount`: Cumulative amount at snapshot time
- `snapshot_at`: Snapshot timestamp

### Achievement
Available achievements in the game.
- `id`: Unique achievement identifier
- `name`: Display name
- `description`: How to unlock
- `ap_reward`: AP awarded when unlocked
- `icon`: Emoji representation
- `condition_type`: Type of unlock condition
- `condition_value`: Threshold value

### PlayerAchievement
Junction table for unlocked achievements.
- `player_id`: Foreign key to Player
- `achievement_id`: Foreign key to Achievement
- `unlocked_at`: Unlock timestamp
- `progress`: Progress toward multi-stage achievements

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Node.js 18+ (for frontend)
- pip and virtualenv

### 1. Clone the Repository

```bash
git clone <repository-url>
cd m2p
```

### 2. Set Up Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE m2p;

# Create user (optional)
CREATE USER m2p_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE m2p TO m2p_user;
```

### 5. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and update the following:

```env
# Update database connection
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/m2p

# Set a secure secret key for production
SECRET_KEY=your-random-secret-key-here

# Update developer wallet address
DEV_WALLET_ADDRESS=your_advc_wallet_address
```

### 6. Initialize the Database

Run the initialization script to create tables and seed achievements:

```bash
cd server
python init_db.py
```

Optional flags:
- `--drop`: Drop all tables before creating (DESTRUCTIVE!)
- `--no-seed`: Skip seeding initial achievements

### 7. Run Database Migrations (Optional)

If you need to manage schema changes:

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

### 8. Run the Development Server

```bash
cd server
python -m flask run
```

Or using the app factory:

```bash
python -c "from server import create_app; app = create_app(); app.run()"
```

The server will start at `http://localhost:5000`

### 9. Verify Installation

Check the health endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "service": "mine-to-play"}
```

## Configuration

### Mining Pools

The system supports three ADVC mining pools (configured in `server/config.py`):

1. **cpu-pool.com**
   - API: `https://cpu-pool.com/api`
   - Endpoint: `/wallet`

2. **rplant.xyz**
   - API: `https://rplant.xyz/api`
   - Endpoint: `/walletEx`

3. **zpool.ca**
   - API: `https://zpool.ca/api`
   - Endpoint: `/wallet`

### Game Constants

- `ADVC_TO_AP_RATE`: 100 (1 ADVC = 100 AP)
- `MIN_VERIFICATION_AMOUNT`: 0.01 ADVC
- `POLL_INTERVAL_SECONDS`: 300 (check pools every 5 minutes)
- `ACHIEVEMENT_CHECK_INTERVAL`: 60 seconds

## API Endpoints

### Health Check
```
GET /health
```

Returns server health status.

### (To be implemented)
- `POST /api/players/register` - Register new player
- `GET /api/players/:id` - Get player profile
- `GET /api/leaderboard` - Get top players
- `GET /api/achievements` - List all achievements
- `POST /api/verify` - Verify wallet ownership
- `GET /api/mining-events/:playerId` - Get mining history

## Development

### Running Tests

```bash
cd server
pytest
```

### Database Migrations

When you modify models:

```bash
flask db migrate -m "Description of your changes"
flask db upgrade
```

### Code Style

Follow PEP 8 guidelines. Use docstrings for all classes and functions.

## Production Deployment

### Environment Variables

Set these for production:

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<strong-random-key>
SESSION_COOKIE_SECURE=True
DATABASE_URL=<production-db-url>
```

### Running with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 'server:create_app()'
```

### Using Docker (Future)

```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Specify your license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-contact-info]

## Acknowledgments

- ADVC mining community
- Pool operators (cpu-pool.com, rplant.xyz, zpool.ca)