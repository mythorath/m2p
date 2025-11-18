# Mine-to-Play Pool Monitoring Service

A high-performance, production-ready background service for monitoring cryptocurrency mining pools and rewarding players in real-time.

## Features

- **Multi-Pool Support**: Monitor multiple mining pools simultaneously (CPU Pool, Rplant, Zpool)
- **Real-Time Rewards**: Automatically detect payouts and award Adventure Points (AP)
- **WebSocket Notifications**: Instant player notifications via SocketIO
- **Robust Error Handling**: Graceful handling of timeouts, API errors, and network issues
- **Performance Metrics**: Track polling success rates, response times, and rewards
- **Flexible Configuration**: Easy environment-based configuration
- **Production Ready**: Systemd service, structured logging, database transactions
- **Extensible**: Simple framework for adding new mining pools

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Linux server (for systemd service)

### Installation

1. Clone and install:
```bash
cd /opt
git clone <repository-url> m2p
cd m2p/deploy
sudo ./install.sh
```

2. Configure environment:
```bash
sudo nano /opt/m2p/.env
# Set your database URL, SocketIO URL, and pool settings
```

3. Initialize database:
```bash
cd /opt/m2p
./venv/bin/python scripts/init_db.py
```

4. Start service:
```bash
sudo systemctl enable pool-poller
sudo systemctl start pool-poller
sudo systemctl status pool-poller
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PoolPoller Service                   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  CPU Pool    │  │   Rplant     │  │    Zpool     │  │
│  │   Parser     │  │   Parser     │  │   Parser     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                 │           │
│         └─────────────────┴─────────────────┘           │
│                         │                               │
│              ┌──────────▼──────────┐                    │
│              │  Process Pool Data  │                    │
│              └──────────┬──────────┘                    │
│                         │                               │
│         ┌───────────────┼───────────────┐               │
│         │               │               │               │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐       │
│  │  Detect     │ │   Award AP  │ │   Notify    │       │
│  │  Payouts    │ │   & Update  │ │   Player    │       │
│  └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │Database │      │  Player  │      │SocketIO  │
   │Snapshots│      │  Stats   │      │  Event   │
   └─────────┘      └──────────┘      └──────────┘
```

## Supported Pools

| Pool | API Status | Currency | Notes |
|------|-----------|----------|-------|
| **CPU Pool** | ✅ Working | ADVC | Direct ADVC payouts |
| **Rplant** | ⚠️ Needs Testing | ADVC | Flexible parser supports multiple formats |
| **Zpool** | ✅ Working | BTC | Auto-converts BTC to ADVC equivalent |

## Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/m2p_db

# Polling (default: 60 seconds)
POLL_INTERVAL_SECONDS=60

# Rewards (default: 100 AP per 1 ADVC)
AP_PER_ADVC=100
MIN_PAYOUT_DELTA=0.0001

# Pools (enable/disable)
CPU_POOL_ENABLED=true
RPLANT_ENABLED=true
ZPOOL_ENABLED=true

# Zpool BTC conversion
BTC_TO_ADVC_RATE=1000000
```

## Database Schema

### Player
Stores player information, wallet addresses, and game stats.

### PoolSnapshot
Historical snapshots of pool statistics for each player.

### MiningEvent
Records of detected mining rewards and AP awarded.

[See full schema in docs/POOL_MONITORING.md](docs/POOL_MONITORING.md#database-schema)

## Usage

### Running as a Service

```bash
# Start
sudo systemctl start pool-poller

# Stop
sudo systemctl stop pool-poller

# Restart
sudo systemctl restart pool-poller

# Status
sudo systemctl status pool-poller

# Logs
sudo journalctl -u pool-poller -f
```

### Running Manually (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Run single test cycle
python scripts/test_poller.py

# Run continuous polling
python -m server.pool_poller
```

### Monitoring

View real-time metrics in logs:

```bash
sudo journalctl -u pool-poller | grep "polling_cycle_complete"
```

Example output:
```json
{
  "event": "polling_cycle_complete",
  "player_count": 150,
  "failures": 2,
  "metrics": {
    "polls_total": 450,
    "polls_successful": 448,
    "rewards_detected": 12,
    "pools": {
      "cpu-pool": {
        "success_rate": 0.99,
        "avg_response_time_ms": 245.67
      }
    }
  }
}
```

## Adding New Pools

Adding support for a new pool takes just 3 steps:

1. **Add configuration** (`.env` and `config.py`)
2. **Create parser function** (in `server/pool_poller.py`)
3. **Register pool** (in `_build_pool_configs()`)

[Full guide in docs/POOL_MONITORING.md](docs/POOL_MONITORING.md#adding-new-pools)

## API Reference

Detailed documentation for each pool's API:

- [CPU Pool API](docs/API_REFERENCE.md#cpu-pool-cpu-poolcom)
- [Rplant API](docs/API_REFERENCE.md#rplant-poolrplantxyz)
- [Zpool API](docs/API_REFERENCE.md#zpool-zpoolca)

## Project Structure

```
m2p/
├── server/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── database.py        # Database connection
│   └── pool_poller.py     # Main polling service
├── scripts/
│   ├── init_db.py         # Database initialization
│   └── test_poller.py     # Testing script
├── deploy/
│   ├── pool-poller.service  # Systemd service
│   └── install.sh         # Installation script
├── docs/
│   ├── POOL_MONITORING.md # Full documentation
│   └── API_REFERENCE.md   # Pool API reference
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Development

### Setting Up Dev Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python scripts/init_db.py

# Run tests
python scripts/test_poller.py
```

### Testing Pool APIs

```bash
# Test CPU Pool
curl "http://cpu-pool.com/api/worker_stats?addr=YOUR_WALLET"

# Test Rplant
curl "https://pool.rplant.xyz/api/walletEx/advc/YOUR_WALLET"

# Test Zpool
curl "https://zpool.ca/api/walletEx?address=YOUR_WALLET"
```

### Running Tests

```bash
# Single polling cycle
python scripts/test_poller.py

# With debug logging
LOG_LEVEL=DEBUG python scripts/test_poller.py
```

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u pool-poller -n 100

# Common fixes:
# 1. Check database connection
# 2. Verify .env file exists and is readable
# 3. Check file permissions
sudo chown -R m2p:m2p /opt/m2p
```

### No rewards detected

```bash
# Check if players are verified
psql m2p_db -c "SELECT id, username, verified FROM players;"

# Enable debug logging
# In .env: LOG_LEVEL=DEBUG
sudo systemctl restart pool-poller
```

### Pool API errors

```bash
# Test pool manually
curl -v "http://cpu-pool.com/api/worker_stats?addr=YOUR_WALLET"

# Disable problematic pool
# In .env: CPU_POOL_ENABLED=false
sudo systemctl restart pool-poller
```

## Performance

- **Concurrent Polling**: Uses asyncio for parallel pool requests
- **Database Efficiency**: Connection pooling and optimized queries
- **Error Isolation**: Pool failures don't affect other pools
- **Resource Limits**: Systemd service limits memory and CPU usage

### Scaling

For large deployments (1000+ players):

1. **Increase polling interval**: `POLL_INTERVAL_SECONDS=120`
2. **Optimize database**: Add indexes, tune PostgreSQL
3. **Distribute load**: Run multiple instances with player sharding
4. **Cache pool responses**: Implement Redis caching layer

## Security

- Non-root service user (`m2p`)
- Restricted file permissions (`.env` is 640)
- Systemd sandboxing enabled
- Input validation on all pool responses
- SQL injection prevention (SQLAlchemy ORM)
- No shell command execution

## Logging

Structured JSON logging with:

- Timestamp (ISO 8601)
- Event type
- Context fields (player_id, pool, etc.)
- Error stack traces

### Log Levels

- **DEBUG**: Detailed polling information
- **INFO**: Polling cycles, rewards detected
- **WARNING**: Pool timeouts, HTTP errors
- **ERROR**: Unexpected errors, database issues

## Monitoring Checklist

- [ ] Service is running: `systemctl is-active pool-poller`
- [ ] Recent successful polls: `journalctl -u pool-poller | grep success`
- [ ] No recent errors: `journalctl -u pool-poller -p err -n 20`
- [ ] Database connectivity: `psql m2p_db -c "SELECT 1"`
- [ ] Rewards being detected: Check `mining_events` table

## Contributing

When adding new pools:

1. Document the API in `docs/API_REFERENCE.md`
2. Add parser function with error handling
3. Add tests in `scripts/test_poller.py`
4. Update this README with pool status

## License

[Add your license here]

## Support

- Documentation: See `docs/` directory
- Issues: Check logs with `journalctl -u pool-poller -f`
- Configuration: Review `.env` and `config.py`

## Roadmap

- [ ] Support for more pools (suggestions welcome)
- [ ] Web dashboard for monitoring
- [ ] Prometheus metrics export
- [ ] Email notifications for large rewards
- [ ] Historical analytics and charts
- [ ] Auto-discovery of new pool APIs
- [ ] Rate limiting and backoff strategies
- [ ] Webhook support for custom integrations

---

Built with ❤️ for the Mine-to-Play community