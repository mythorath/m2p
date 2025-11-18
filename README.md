# Mine to Play (M2P)

> A blockchain-integrated gaming platform with pool mining mechanics and achievement systems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-blue)](https://www.python.org/)

## Overview

Mine to Play (M2P) is an innovative gaming platform that combines traditional gaming mechanics with blockchain technology. Players can join mining pools, complete achievements, earn rewards, and interact with the game through a secure, wallet-based authentication system.

## Features

### Core Features
- **Wallet Integration**: Secure player authentication using blockchain wallets
- **Pool System**: Join and manage mining pools with dynamic reward distribution
- **Achievement System**: Unlock achievements and earn Achievement Points (AP)
- **Real-time Updates**: WebSocket-based live game state synchronization
- **Player Verification**: Multi-tier verification system for enhanced security
- **Leaderboards**: Competitive rankings based on AP and achievements

### Pool Features
- Multiple pool types with unique characteristics
- Dynamic difficulty adjustment
- Reward distribution based on contribution
- Pool statistics and analytics
- Pool ownership and management

### Achievement System
- Tiered achievements (Bronze, Silver, Gold, Platinum, Diamond)
- Progressive unlocking mechanics
- AP rewards for completion
- Achievement tracking and statistics

### Security Features
- Wallet-based authentication
- SQL injection prevention
- XSS protection
- Rate limiting
- Input validation and sanitization
- CSRF protection

## Quick Start

### Prerequisites

- **Node.js** >= 18.0.0
- **Python** >= 3.9
- **PostgreSQL** >= 13
- **Redis** >= 6.0 (for caching and sessions)
- **Nginx** (for production deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/m2p.git
   cd m2p
   ```

2. **Install dependencies**
   ```bash
   # Backend
   cd server
   npm install

   # Frontend
   cd ../client
   npm install
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   cd server
   npm run db:migrate
   npm run db:seed
   ```

5. **Start development servers**
   ```bash
   # Terminal 1 - Backend
   cd server
   npm run dev

   # Terminal 2 - Frontend
   cd client
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Docs: http://localhost:5000/api-docs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   React    │  │  Web3/Wallet │  │  WebSocket      │    │
│  │   Frontend │  │  Integration │  │  Client         │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Nginx/SSL    │
                    └───────┬────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Application Layer                       │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Express  │  │   WebSocket  │  │   Auth Layer    │    │
│  │   REST API │  │   Server     │  │   (Wallet)      │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Service Layer                           │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   Pool     │  │  Achievement │  │   Player        │    │
│  │   Manager  │  │  System      │  │   Service       │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Data Layer                              │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │ PostgreSQL │  │    Redis     │  │   Blockchain    │    │
│  │  Database  │  │    Cache     │  │   (Read-only)   │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **Web3.js / Ethers.js** - Blockchain interaction
- **Socket.io-client** - Real-time communication

### Backend
- **Node.js** - Runtime environment
- **Express** - Web framework
- **TypeScript** - Type safety
- **Socket.io** - WebSocket server
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **Prisma** - ORM and database migrations

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and load balancing
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **Let's Encrypt** - SSL certificates

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Jest** - Unit testing
- **Supertest** - API testing
- **Playwright** - E2E testing

## Project Structure

```
m2p/
├── client/                 # Frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── utils/         # Utility functions
│   │   └── types/         # TypeScript types
│   ├── public/            # Static assets
│   └── package.json
│
├── server/                # Backend application
│   ├── src/
│   │   ├── controllers/   # Request handlers
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   ├── middleware/    # Express middleware
│   │   ├── routes/        # API routes
│   │   ├── websocket/     # WebSocket handlers
│   │   └── utils/         # Utility functions
│   ├── prisma/            # Database schema and migrations
│   └── package.json
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System design
│   ├── API.md             # API documentation
│   ├── DEPLOYMENT.md      # Deployment guide
│   ├── DEVELOPMENT.md     # Development setup
│   ├── POOL_INTEGRATION.md    # Pool integration guide
│   ├── ACHIEVEMENT_GUIDE.md   # Achievement creation guide
│   ├── SECURITY.md        # Security best practices
│   ├── TROUBLESHOOTING.md     # Common issues and solutions
│   └── PERFORMANCE.md     # Performance optimization
│
├── deploy/                # Deployment configuration
│   ├── docker/
│   │   ├── Dockerfile.server
│   │   ├── Dockerfile.client
│   │   └── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   ├── systemd/
│   │   ├── m2p-server.service
│   │   └── m2p-worker.service
│   ├── monitoring/
│   │   ├── prometheus.yml
│   │   └── grafana-dashboard.json
│   └── ssl/
│       └── setup-ssl.sh
│
├── scripts/               # Utility scripts
│   ├── admin.py          # Admin CLI tool
│   ├── backup-db.sh      # Database backup
│   ├── restore-db.sh     # Database restore
│   └── health-check.sh   # Health monitoring
│
├── .env.example          # Environment variables template
├── CHANGELOG.md          # Version history
└── README.md             # This file
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and component interactions
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Development Setup](docs/DEVELOPMENT.md)** - Local development environment
- **[Pool Integration](docs/POOL_INTEGRATION.md)** - How to add new pool types
- **[Achievement Guide](docs/ACHIEVEMENT_GUIDE.md)** - Creating custom achievements
- **[Security Guide](docs/SECURITY.md)** - Security best practices
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Performance Guide](docs/PERFORMANCE.md)** - Optimization strategies

## API Overview

The API is RESTful and returns JSON responses. All endpoints are prefixed with `/api/v1`.

### Key Endpoints

- `POST /api/v1/auth/connect` - Connect wallet
- `GET /api/v1/pools` - List all pools
- `POST /api/v1/pools/:id/join` - Join a pool
- `GET /api/v1/achievements` - List achievements
- `GET /api/v1/players/:wallet` - Get player profile
- `GET /api/v1/leaderboard` - Get leaderboard

See [API.md](docs/API.md) for complete documentation.

## WebSocket Events

Real-time updates are provided via WebSocket connection at `ws://localhost:5000`.

### Client Events
- `join_pool` - Join a mining pool
- `submit_share` - Submit mining work
- `request_stats` - Request statistics update

### Server Events
- `pool_update` - Pool state changed
- `achievement_unlocked` - Achievement earned
- `leaderboard_update` - Leaderboard changed
- `reward_distributed` - Rewards distributed

See [API.md](docs/API.md) for complete WebSocket documentation.

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass (`npm test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow the existing code style
- Use TypeScript for all new code
- Write meaningful commit messages
- Add JSDoc comments for functions
- Update documentation for user-facing changes

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Run `npm test` before submitting PR
- Include integration tests for API endpoints

### Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with your changes
3. The PR will be merged once you have approval from maintainers

## Development

### Running Tests

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Test coverage
npm run test:coverage
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

### Database Migrations

```bash
# Create migration
npm run db:migrate:create

# Run migrations
npm run db:migrate

# Rollback migration
npm run db:migrate:rollback

# Seed database
npm run db:seed
```

## Deployment

For production deployment, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

### Quick Deploy with Docker

```bash
cd deploy/docker
docker-compose up -d
```

### Environment Variables

See [.env.example](.env.example) for all available configuration options.

## Monitoring

- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3001
- **Health Check**: http://localhost:5000/health

## Security

Security is a top priority. Please report security vulnerabilities to security@m2p.example.com.

See [SECURITY.md](docs/SECURITY.md) for security best practices.

## Performance

The platform is designed to handle:
- 10,000+ concurrent players
- 100+ active pools
- 1,000+ requests per second
- Sub-100ms API response times

See [PERFORMANCE.md](docs/PERFORMANCE.md) for optimization strategies.

## Roadmap

### Version 1.0 (Current)
- [x] Core pool mechanics
- [x] Achievement system
- [x] Wallet authentication
- [x] WebSocket real-time updates
- [x] Basic leaderboards

### Version 1.1 (Planned)
- [ ] Advanced pool types
- [ ] Guild system
- [ ] Trading marketplace
- [ ] Mobile app
- [ ] Multi-chain support

### Version 2.0 (Future)
- [ ] NFT integration
- [ ] DAO governance
- [ ] Cross-pool tournaments
- [ ] AI-powered matchmaking

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors
- Inspired by DeFi gaming innovations
- Built with love for the blockchain gaming community

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/m2p/issues)
- **Discord**: [Join our community](https://discord.gg/m2p)
- **Twitter**: [@M2PGame](https://twitter.com/M2PGame)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and migration guides.

---

**Built with ❤️ by the M2P Team**
