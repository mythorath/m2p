# Pool Monitoring Service Documentation

## Overview

The Pool Monitoring Service is a background service that continuously monitors multiple cryptocurrency mining pools for player rewards. When a payout is detected, it automatically awards in-game Adventure Points (AP) to players and sends real-time notifications via WebSocket.

## Architecture

### Components

1. **PoolPoller** - Main service class that orchestrates polling
2. **Database Models** - SQLAlchemy models for Player, PoolSnapshot, and MiningEvent
3. **Pool Parsers** - Pool-specific response parsers
4. **Metrics Tracking** - Performance and reliability monitoring
5. **WebSocket Notifications** - Real-time player notifications

### Flow

```
┌─────────────────┐
│  PoolPoller     │
│  (Main Loop)    │
└────────┬────────┘
         │
         ├─> Poll All Players (every 60s)
         │   │
         │   ├─> Fetch pool stats (HTTP GET)
         │   │   ├─> cpu-pool.com
         │   │   ├─> rplant.xyz
         │   │   └─> zpool.ca
         │   │
         │   ├─> Parse responses
         │   │
         │   └─> Process data
         │       │
         │       ├─> Compare with last snapshot
         │       ├─> Detect payout delta
         │       ├─> Award AP if delta > threshold
         │       ├─> Create MiningEvent
         │       ├─> Notify player (WebSocket)
         │       └─> Save new snapshot
         │
         └─> Sleep until next cycle
```

## Supported Pools

### 1. CPU Pool (cpu-pool.com)

**API Endpoint:** `http://cpu-pool.com/api/worker_stats?addr={wallet}`

**Response Format:**
```json
{
  "totalHash": 12345.67,
  "totalShares": 98765,
  "immature": 0.5,
  "balance": 1.2,
  "paid": 10.5
}
```

**Tracked Field:** `paid` (cumulative payouts in ADVC)

### 2. Rplant (pool.rplant.xyz)

**API Endpoint:** `https://pool.rplant.xyz/api/walletEx/advc/{wallet}`

**Response Format:** *To be confirmed - parser supports multiple formats*

**Tracked Field:** `paid` or equivalent

**Note:** This pool's API format requires discovery. The parser is flexible and attempts multiple response structures.

### 3. Zpool (zpool.ca)

**API Endpoint:** `https://zpool.ca/api/walletEx?address={wallet}`

**Response Format:**
```json
{
  "currency": "BTC",
  "unsold": 0.00001,
  "balance": 0.00002,
  "unpaid": 0.00003,
  "paid": 0.0005,
  "total": 0.00056
}
```

**Tracked Field:** `paid` (in BTC, converted to ADVC)

**Important:** Zpool pays in BTC, so conversion to ADVC equivalent is required using `BTC_TO_ADVC_RATE` configuration.

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/m2p_db

# SocketIO
SOCKETIO_URL=http://localhost:3000

# Polling
POLL_INTERVAL_SECONDS=60
POOL_REQUEST_TIMEOUT=10

# Rewards
AP_PER_ADVC=100
MIN_PAYOUT_DELTA=0.0001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Pools
CPU_POOL_ENABLED=true
CPU_POOL_URL=http://cpu-pool.com/api/worker_stats

RPLANT_ENABLED=true
RPLANT_URL=https://pool.rplant.xyz/api/walletEx/advc

ZPOOL_ENABLED=true
ZPOOL_URL=https://zpool.ca/api/walletEx

BTC_TO_ADVC_RATE=1000000
```

### Key Parameters

- **POLL_INTERVAL_SECONDS**: How often to poll all players (default: 60 seconds)
- **POOL_REQUEST_TIMEOUT**: HTTP request timeout per pool (default: 10 seconds)
- **AP_PER_ADVC**: Adventure Points awarded per 1 ADVC mined (default: 100)
- **MIN_PAYOUT_DELTA**: Minimum payout change to trigger reward (default: 0.0001 ADVC)

## Database Schema

### Player Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| username | String | Unique username |
| email | String | Player email |
| wallet_address | String | ADVC wallet address |
| total_ap | Float | Total Adventure Points |
| total_advc_mined | Float | Total ADVC mined |
| verified | Boolean | Account verified status |
| active | Boolean | Account active status |
| last_mining_event | DateTime | Last reward timestamp |

### PoolSnapshot Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| player_id | Integer | Foreign key to Player |
| pool_name | String | Pool identifier |
| paid | Float | Cumulative payouts |
| total_hash | Float | Total hashrate |
| balance | Float | Current balance |
| snapshot_time | DateTime | Snapshot timestamp |

### MiningEvent Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| player_id | Integer | Foreign key to Player |
| pool_name | String | Pool identifier |
| advc_amount | Float | ADVC paid out |
| ap_awarded | Float | AP awarded |
| previous_paid | Float | Previous cumulative paid |
| current_paid | Float | New cumulative paid |
| event_time | DateTime | Event timestamp |
| notified | Boolean | WebSocket notification sent |

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

### Steps

1. **Clone the repository:**
   ```bash
   cd /opt
   git clone <repository-url> m2p
   cd m2p
   ```

2. **Run the installation script:**
   ```bash
   cd deploy
   sudo ./install.sh
   ```

3. **Configure environment:**
   ```bash
   sudo nano /opt/m2p/.env
   # Edit with your database credentials and settings
   ```

4. **Initialize database:**
   ```bash
   cd /opt/m2p
   ./venv/bin/python scripts/init_db.py
   ```

5. **Enable and start service:**
   ```bash
   sudo systemctl enable pool-poller
   sudo systemctl start pool-poller
   ```

6. **Check status:**
   ```bash
   sudo systemctl status pool-poller
   sudo journalctl -u pool-poller -f
   ```

## Adding New Pools

To add support for a new mining pool:

### 1. Add Configuration

Add environment variables to `.env`:

```bash
NEWPOOL_ENABLED=true
NEWPOOL_URL=https://newpool.com/api/stats
```

Add to `config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    newpool_enabled: bool = True
    newpool_url: str = "https://newpool.com/api/stats"
```

### 2. Create Parser Function

Add a parser method to `PoolPoller` class in `server/pool_poller.py`:

```python
def parse_newpool(self, data: Dict[str, Any]) -> Dict[str, float]:
    """
    Parse newpool.com API response.

    Expected response: {your_format_here}

    Returns:
        Dict with 'paid' field (cumulative payouts in ADVC)
    """
    try:
        return {
            "paid": float(data.get("total_paid", 0.0)),
            "balance": float(data.get("balance", 0.0)),
            # Add other fields as needed
        }
    except (ValueError, TypeError) as e:
        logger.error("newpool_parse_error", error=str(e), data=data)
        return {"paid": 0.0}
```

### 3. Register Pool Configuration

Add to `_build_pool_configs()` method:

```python
def _build_pool_configs(self) -> List[Dict[str, Any]]:
    """Build list of enabled pool configurations."""
    configs = []

    # ... existing pools ...

    if settings.newpool_enabled:
        configs.append({
            "name": "newpool",
            "url_template": settings.newpool_url + "?wallet={wallet}",
            "parser": self.parse_newpool,
        })

    return configs
```

### 4. Test

Test with a single polling cycle:

```bash
./scripts/test_poller.py
```

### 5. Deploy

Restart the service:

```bash
sudo systemctl restart pool-poller
sudo journalctl -u pool-poller -f
```

## API Response Examples

### CPU Pool

```bash
curl "http://cpu-pool.com/api/worker_stats?addr=YOUR_WALLET"
```

Response:
```json
{
  "totalHash": 12345.67,
  "totalShares": 98765,
  "immature": 0.5,
  "balance": 1.2,
  "paid": 10.5
}
```

### Zpool

```bash
curl "https://zpool.ca/api/walletEx?address=YOUR_WALLET"
```

Response:
```json
{
  "currency": "BTC",
  "unsold": 0.00001,
  "balance": 0.00002,
  "unpaid": 0.00003,
  "paid": 0.0005,
  "total": 0.00056
}
```

## Monitoring

### Metrics

The service tracks:
- Total polls
- Successful/failed requests per pool
- Average response time per pool
- Total rewards detected
- Uptime

Access metrics via logs:

```bash
sudo journalctl -u pool-poller | grep "polling_cycle_complete"
```

### Health Checks

Check if service is running:

```bash
sudo systemctl is-active pool-poller
```

Check recent errors:

```bash
sudo journalctl -u pool-poller -p err -n 50
```

### Performance Tuning

Adjust polling interval based on load:

```bash
# In .env
POLL_INTERVAL_SECONDS=120  # Poll every 2 minutes instead of 1
```

Adjust timeout for slow pools:

```bash
POOL_REQUEST_TIMEOUT=20  # Increase to 20 seconds
```

## Troubleshooting

### Service won't start

Check logs:
```bash
sudo journalctl -u pool-poller -n 100
```

Common issues:
- Database connection failed (check DATABASE_URL)
- Missing dependencies (reinstall with pip)
- Permission errors (check file ownership)

### No rewards detected

1. Check if players are verified:
   ```sql
   SELECT id, username, verified, active FROM players;
   ```

2. Check pool snapshots:
   ```sql
   SELECT * FROM pool_snapshots ORDER BY snapshot_time DESC LIMIT 10;
   ```

3. Enable debug logging:
   ```bash
   # In .env
   LOG_LEVEL=DEBUG
   sudo systemctl restart pool-poller
   ```

### Pool API errors

Check pool availability:
```bash
curl -v "http://cpu-pool.com/api/worker_stats?addr=YOUR_WALLET"
```

Disable problematic pools:
```bash
# In .env
CPU_POOL_ENABLED=false
```

## Security Considerations

1. **Database Credentials**: Store in `.env` with restricted permissions (chmod 640)
2. **Service User**: Runs as non-root user `m2p`
3. **Sandboxing**: Systemd service has security restrictions enabled
4. **Rate Limiting**: Consider implementing rate limiting for pool APIs
5. **Input Validation**: All pool responses are validated before processing

## Maintenance

### Backup Database

```bash
pg_dump m2p_db > backup_$(date +%Y%m%d).sql
```

### Clean Old Snapshots

```sql
-- Keep only last 30 days of snapshots
DELETE FROM pool_snapshots
WHERE snapshot_time < NOW() - INTERVAL '30 days';
```

### Update Dependencies

```bash
source /opt/m2p/venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart pool-poller
```

## Development

### Running Locally

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

# Run test cycle
python scripts/test_poller.py

# Run service
python -m server.pool_poller
```

### Testing

```bash
# Run test polling cycle
python scripts/test_poller.py

# Run with debug logging
LOG_LEVEL=DEBUG python -m server.pool_poller
```

## Support

For issues or questions:
1. Check logs: `journalctl -u pool-poller -f`
2. Review configuration in `.env`
3. Test pool APIs manually with curl
4. Check database connectivity
5. Verify player verification status

## License

[Add your license here]
