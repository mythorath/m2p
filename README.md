# Mine to Play (M2P) - Complete Integrated Platform

> A blockchain-integrated gaming platform combining pool mining mechanics, achievement systems, and real-time gameplay

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## Overview

Mine to Play (M2P) is a revolutionary gaming platform that combines traditional gaming mechanics with blockchain technology. Players can join mining pools, complete achievements, earn rewards, and interact with the game through a secure, wallet-based authentication system.

This repository contains the **complete integrated system** with all features from multiple development phases:
- ✅ Database foundation and models
- ✅ Flask API server with WebSocket support
- ✅ Pool monitoring and management
- ✅ Wallet verification system
- ✅ Achievement tracking and unlocking
- ✅ Leaderboard system with real-time updates
- ✅ React game client with animations
- ✅ Game visualizations and effects
- ✅ Comprehensive test suite
- ✅ Complete documentation and deployment guides

## Quick Start

### Prerequisites

- **Python** >= 3.9
- **Node.js** >= 16.0
- **npm** >= 8.0
- **PostgreSQL** >= 13 (or SQLite for development)
- **Redis** >= 6.0 (optional, for production caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/m2p.git
   cd m2p
   ```

2. **Setup Backend**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Setup environment variables
   cp server/.env.example server/.env
   # Edit server/.env with your configuration

   # Initialize database
   cd server
   python
   >>> from app import app, db
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

3. **Setup Frontend**
   ```bash
   cd client
   npm install

   # Setup environment
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Run the Application**

   **Backend** (Terminal 1):
   ```bash
   cd server
   chmod +x run.sh
   ./run.sh
   # Or manually:
   # python app.py
   ```

   **Frontend** (Terminal 2):
   ```bash
   cd client
   npm start
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Docs: http://localhost:5000/api (when enabled)

## Features

### Core Game Features
- **Wallet Integration**: Secure player authentication using blockchain wallet signatures
- **Pool System**: Join and manage mining pools with dynamic reward distribution
- **Achievement System**: Unlock achievements and earn Achievement Points (AP)
- **Real-time Updates**: WebSocket-based live game state synchronization
- **Player Verification**: Multi-tier verification system for enhanced security
- **Leaderboards**: Competitive rankings based on AP, hashrate, and rewards
- **Reward System**: Automated reward distribution based on pool contributions

### Frontend Features
- **Interactive Game View**: Animated mining scenes with sprite-based characters
- **Real-time Notifications**: Instant reward and achievement popups
- **Responsive Design**: Mobile-friendly dark theme with glassmorphism effects
- **Audio Controls**: Background music and sound effects
- **Loading States**: Smooth loading animations and state management
- **Statistics Dashboard**: Comprehensive player and pool statistics
- **Achievement Gallery**: Visual achievement tracking with progress bars

### Backend Features
- **RESTful API**: Complete REST API for all game operations
- **WebSocket Server**: Real-time bidirectional communication
- **Database Models**: Comprehensive SQLAlchemy models for all entities
- **Rate Limiting**: Protection against abuse and spam
- **Error Handling**: Graceful error handling with detailed logging
- **Security**: Input validation, SQL injection prevention, XSS protection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   React    │  │  WebSocket   │  │  Animations     │    │
│  │   App      │  │  Client      │  │  & Effects      │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   API Gateway  │
                    │   (Optional)   │
                    └───────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Application Layer                       │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Flask    │  │   Socket.IO  │  │   Rate Limiter  │    │
│  │   REST API │  │   WebSocket  │  │                 │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Business Layer                          │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Pool     │  │  Achievement │  │   Verification  │    │
│  │  Manager   │  │  System      │  │   Service       │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                       Data Layer                             │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │ PostgreSQL │  │    Redis     │  │   File Storage  │    │
│  │  Database  │  │   (Cache)    │  │                 │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
m2p/
├── client/                 # React frontend application
│   ├── src/
│   │   ├── components/    # React components (GameView, Leaderboard, etc.)
│   │   ├── hooks/         # Custom hooks (usePlayer, useWebSocket)
│   │   ├── services/      # API and WebSocket services
│   │   ├── context/       # React context for state management
│   │   └── animations/    # Animation configurations
│   ├── public/            # Static assets and sounds
│   └── package.json
│
├── server/                # Flask backend application
│   ├── app.py             # Main Flask application with routes
│   ├── models.py          # SQLAlchemy database models
│   ├── tests/             # Backend test suite
│   └── run.sh             # Server startup script
│
├── docs/                  # Comprehensive documentation
│   ├── ARCHITECTURE.md    # System architecture guide
│   ├── API.md             # Complete API reference
│   ├── DEPLOYMENT.md      # Deployment instructions
│   ├── DEVELOPMENT.md     # Development setup guide
│   ├── POOL_INTEGRATION.md    # Pool integration guide
│   ├── ACHIEVEMENT_GUIDE.md   # Achievement creation guide
│   ├── SECURITY.md        # Security best practices
│   ├── TROUBLESHOOTING.md # Common issues and solutions
│   └── PERFORMANCE.md     # Performance optimization
│
├── deploy/                # Deployment configuration
│   ├── docker/           # Docker configurations
│   ├── nginx/            # Nginx configuration
│   ├── systemd/          # Systemd service files
│   ├── monitoring/       # Prometheus and Grafana configs
│   └── ssl/              # SSL setup scripts
│
├── scripts/               # Utility scripts
│   ├── admin.py          # Admin CLI tool
│   ├── backup-db.sh      # Database backup script
│   ├── restore-db.sh     # Database restore script
│   └── health-check.sh   # Health monitoring script
│
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── requirements-test.txt # Testing dependencies
├── pytest.ini            # Pytest configuration
├── Makefile              # Common tasks automation
├── TESTING.md            # Testing documentation
└── CHANGELOG.md          # Version history
```

## API Overview

### REST Endpoints

#### Authentication
- `POST /api/register` - Register new player with wallet
- `POST /api/login` - Login with wallet and password
- `POST /api/verify` - Verify wallet ownership

#### Player Management
- `GET /api/players/<wallet>` - Get player profile
- `PUT /api/players/<wallet>` - Update player profile
- `GET /api/players/<wallet>/stats` - Get player statistics

#### Pools
- `GET /api/pools` - List all pools
- `GET /api/pools/<id>` - Get pool details
- `POST /api/pools/<id>/join` - Join a pool
- `POST /api/pools/<id>/leave` - Leave a pool

#### Achievements
- `GET /api/achievements` - List all achievements
- `GET /api/players/<wallet>/achievements` - Get player achievements
- `GET /api/achievements/<id>` - Get achievement details

#### Leaderboard
- `GET /api/leaderboard` - Get global leaderboard
- `GET /api/leaderboard/weekly` - Get weekly leaderboard
- `GET /api/leaderboard/daily` - Get daily leaderboard

### WebSocket Events

#### Client → Server
- `join_pool` - Join a pool room
- `submit_share` - Submit mining work
- `request_stats` - Request statistics update

#### Server → Client
- `mining_reward` - New mining reward received
- `achievement_unlocked` - Achievement unlocked
- `pool_update` - Pool state changed
- `leaderboard_update` - Leaderboard changed

See [API.md](docs/API.md) for complete API documentation.

## Development

### Running Tests

```bash
# Backend tests
cd server
pytest

# With coverage
pytest --cov=. --cov-report=html

# Frontend tests
cd client
npm test

# E2E tests
npm run test:e2e
```

### Code Quality

```bash
# Python linting
cd server
pylint app.py models.py

# JavaScript linting
cd client
npm run lint

# Format code
npm run format
```

## Deployment

### Docker Deployment (Recommended)

```bash
cd deploy/docker
docker-compose up -d
```

### Manual Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed production deployment instructions including:
- Database setup
- Nginx configuration
- SSL certificates
- Systemd services
- Monitoring setup
- Backup strategies

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Development](docs/DEVELOPMENT.md)** - Development environment setup
- **[Pool Integration](docs/POOL_INTEGRATION.md)** - Adding custom pool types
- **[Achievement Guide](docs/ACHIEVEMENT_GUIDE.md)** - Creating achievements
- **[Security](docs/SECURITY.md)** - Security best practices
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues
- **[Performance](docs/PERFORMANCE.md)** - Optimization strategies
- **[Testing](TESTING.md)** - Test suite documentation

## Admin Tools

### CLI Admin Tool

```bash
# Verify a player
python scripts/admin.py verify-player <wallet> --level 2

# Award achievement points
python scripts/admin.py award-ap <wallet> 100

# Ban/unban player
python scripts/admin.py ban-player <wallet> --reason "Cheating"
python scripts/admin.py unban-player <wallet>

# Show system stats
python scripts/admin.py stats

# List top players
python scripts/admin.py list-players --limit 50 --sort-by ap
```

### Database Backup

```bash
# Backup database
./scripts/backup-db.sh

# Restore from backup
./scripts/restore-db.sh /path/to/backup.sql
```

## Monitoring

- **Health Check**: http://localhost:5000/health
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3001

## Security

- Wallet-based authentication with signature verification
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- Rate limiting
- CSRF protection
- Secure password hashing
- Environment variable management

See [SECURITY.md](docs/SECURITY.md) for security best practices.

## Performance

Target performance metrics:
- API Response Time: < 200ms (p95)
- WebSocket Latency: < 100ms
- Throughput: > 1000 req/s
- Concurrent Users: 10,000+

See [PERFORMANCE.md](docs/PERFORMANCE.md) for optimization strategies.

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/m2p/issues)
- **Email**: support@m2p.example.com

## Acknowledgments

This project integrates work from multiple development phases:
- Phase 1: Database foundation and models
- Phase 2: Flask API and WebSocket server
- Phase 3: Pool monitoring service
- Phase 4: Wallet verification system
- Phase 5: Achievement tracking system
- Phase 6: Leaderboard implementation
- Phase 7: React game client
- Phase 8: Game visualizations and animations
- Phase 9: Comprehensive test suite
- Phase 10: Documentation and deployment infrastructure

---

**Built with ❤️ for the blockchain gaming community**
