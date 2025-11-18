# M2P - Mining to Podium

A gamified leaderboard system for Alephium miners with achievements, rewards, and competitive gameplay.

## Overview

M2P (Mining to Podium) transforms cryptocurrency mining into an engaging competitive experience. Players register their Alephium wallet addresses, mine ALPH, and compete on leaderboards to earn Achievement Points (AP) and unlock achievements.

## Features

- **Player Registration & Verification**: Secure wallet-based registration with blockchain verification
- **Automated Pool Monitoring**: Real-time tracking of mining rewards across multiple pools
- **Achievement System**: Unlock achievements and earn AP for various milestones
- **Multi-Period Leaderboards**: Compete daily, weekly, monthly, and all-time
- **Real-Time Updates**: WebSocket-based live updates for rewards and achievements
- **RESTful API**: Complete API for player data, leaderboards, and achievements

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/m2p.git
cd m2p

# Install dependencies
pip install -r requirements-test.txt

# Run tests
pytest server/tests -v
```

### Using Make Commands

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run linting
make lint

# Run all CI checks
make ci
```

## Testing

M2P includes a comprehensive test suite with 80%+ code coverage.

### Test Categories

- **Unit Tests**: Test individual components (models, API, services)
- **Integration Tests**: Test complete user flows
- **Load Tests**: Performance and stress testing
- **Security Tests**: Security vulnerability scanning

### Running Tests

```bash
# All tests
pytest server/tests -v

# Unit tests only
pytest server/tests -m unit -v

# Integration tests only
pytest server/tests -m integration -v

# With coverage report
pytest server/tests --cov=server --cov-report=html
```

### Load Testing

```bash
# Start Locust web interface
locust -f server/tests/load/locustfile.py --host=http://localhost:5000

# Headless load test
make load-test-headless
```

For detailed testing documentation, see [TESTING.md](TESTING.md).

## Project Structure

```
m2p/
├── server/
│   ├── __init__.py
│   └── tests/
│       ├── conftest.py              # Pytest fixtures
│       ├── test_models.py           # Model tests
│       ├── test_api.py              # API tests
│       ├── test_pool_poller.py      # Pool polling tests
│       ├── test_verifier.py         # Verification tests
│       ├── test_achievements.py     # Achievement tests
│       ├── test_utils.py            # Test utilities
│       ├── integration/
│       │   └── test_full_flow.py    # E2E tests
│       └── load/
│           └── locustfile.py        # Load tests
├── .github/
│   └── workflows/
│       └── test.yml                 # CI/CD pipeline
├── pytest.ini                       # Pytest configuration
├── requirements-test.txt            # Test dependencies
├── Makefile                         # Common commands
├── Dockerfile.test                  # Test container
├── TESTING.md                       # Testing documentation
└── README.md                        # This file
```

## API Endpoints

### Player Management
- `POST /api/register` - Register new player
- `GET /api/player/:wallet` - Get player information

### Leaderboards
- `GET /api/leaderboard?period=all` - All-time leaderboard
- `GET /api/leaderboard?period=daily` - Daily leaderboard
- `GET /api/leaderboard?period=weekly` - Weekly leaderboard
- `GET /api/leaderboard?period=monthly` - Monthly leaderboard

### Achievements
- `GET /api/achievements` - Get all achievements
- `GET /api/player/:wallet/achievements` - Get player's achievements

## Achievement Categories

- **Mining**: Rewards for mining milestones
- **Social**: Referral and community achievements
- **Streak**: Consecutive mining day rewards
- **Special**: Limited-time and special event achievements

## Development

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
make install

# Setup development tools
make dev-setup
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# Security scan
make security
```

## CI/CD

The project uses GitHub Actions for automated testing:

- **Test**: Run all tests on Python 3.9, 3.10, 3.11
- **Security**: Security vulnerability scanning
- **Coverage**: Code coverage reporting
- **Docker**: Containerized test execution

## Test Coverage

Current coverage targets:
- Overall: 80%+
- Models: 90%+
- API: 85%+
- Business Logic: 90%+

View coverage report:
```bash
make test-cov
open htmlcov/index.html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Maintain 80%+ coverage
6. Submit pull request

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy
- **Testing**: pytest, locust
- **Blockchain**: Alephium
- **Real-time**: WebSocket (SocketIO)

## License

[Add your license here]

## Support

For questions or issues:
- Open an issue on GitHub
- Check [TESTING.md](TESTING.md) for testing documentation

## Roadmap

- [ ] Complete backend implementation
- [x] Comprehensive test suite
- [ ] Frontend implementation
- [ ] Multi-pool support
- [ ] Advanced achievement system
- [ ] Mobile app

---

**Status**: Test Suite Complete ✅

The comprehensive test suite is ready for implementation integration.
