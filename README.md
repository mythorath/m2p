# M2P Wallet Verification System

A robust wallet verification service for the Myth to Profit (M2P) game that validates ADVC cryptocurrency donations on the blockchain.

## Features

- **Multi-Method Verification**: Three independent verification methods with automatic fallback
  1. ADVC Explorer API
  2. Pool Payment History API
  3. Web Scraping (fallback)

- **Automatic Verification Loop**: Background service that checks pending verifications every 5 minutes

- **Real-time Notifications**: WebSocket support for instant player notifications

- **AP Refund System**: Automatic Adventure Points (AP) credit upon successful verification

- **Admin Dashboard**: Complete admin API for manual verification and monitoring

- **Security Features**:
  - Transaction confirmation requirements (minimum 6 blocks)
  - 24-hour verification timeout
  - Prevent verification amount reuse
  - Admin API authentication

## Architecture

```
m2p/
├── server/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask application with endpoints
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   └── verifier.py          # Wallet verification service
├── init_db.py               # Database initialization script
├── setup.sh                 # Automated setup script
├── requirements.txt         # Python dependencies
├── m2p-verifier.service     # Systemd service file
├── .env.example             # Example environment configuration
└── README.md                # This file
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd m2p
./setup.sh
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Required settings
DEV_WALLET_ADDRESS=your_actual_dev_wallet_address
ADMIN_API_KEY=your_secure_random_api_key
SECRET_KEY=your_flask_secret_key

# Optional settings (defaults provided)
DATABASE_URL=sqlite:///m2p.db
VERIFICATION_TIMEOUT_HOURS=24
VERIFICATION_CHECK_INTERVAL_MINUTES=5
```

### 3. Initialize Database

```bash
source venv/bin/activate
python init_db.py
```

### 4. Run Application

```bash
# Development
python -m server.app

# Production (see DEPLOYMENT.md)
sudo systemctl start m2p-verifier
```

## API Endpoints

### Public Endpoints

#### POST /api/register
Register a new player for wallet verification.

**Request:**
```json
{
  "wallet_address": "string"
}
```

**Response:**
```json
{
  "success": true,
  "player": {...},
  "verification_amount": 0.1234,
  "message": "Please send exactly 0.1234 ADVC to verify"
}
```

#### GET /api/player/:wallet_address
Get player information and verification status.

**Response:**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "wallet_address": "...",
    "verified": false,
    "verification_amount": 0.1234,
    "total_ap": 0.0
  }
}
```

#### POST /api/verify-now
Manually trigger verification check for a player.

**Request:**
```json
{
  "wallet_address": "string"
}
```

**Response:**
```json
{
  "success": true,
  "verified": true,
  "player": {...},
  "message": "Verification successful!"
}
```

### Admin Endpoints

All admin endpoints require authentication via `Authorization: Bearer <ADMIN_API_KEY>` header.

#### POST /admin/verify-player
Manually verify a player (bypass automatic verification).

**Request:**
```json
{
  "wallet_address": "string",
  "tx_hash": "optional_transaction_hash"
}
```

#### GET /admin/players
Get all players with optional filtering.

**Query Parameters:**
- `verified`: Filter by verification status (true/false)
- `limit`: Number of results (default: 100)
- `offset`: Pagination offset (default: 0)

#### GET /admin/verification-logs
Get verification attempt logs.

**Query Parameters:**
- `wallet_address`: Filter by wallet address
- `status`: Filter by status (success/failed/expired/error)
- `limit`: Number of results (default: 100)
- `offset`: Pagination offset (default: 0)

## WebSocket Events

### Client → Server

**connect**: Establish WebSocket connection
```javascript
socket.connect();
```

**join**: Join wallet address room for notifications
```javascript
socket.emit('join', { wallet_address: 'your_wallet' });
```

### Server → Client

**verification_complete**: Verification successful
```json
{
  "wallet_address": "...",
  "tx_hash": "...",
  "ap_credited": 100.0,
  "total_ap": 100.0,
  "message": "Verification successful! 100 AP credited."
}
```

**verification_expired**: Verification challenge expired
```json
{
  "wallet_address": "...",
  "message": "Verification challenge expired. Please register again."
}
```

## Verification Process

1. **Player Registration**
   - Player provides wallet address
   - System generates random verification amount (0.1-1.0 ADVC)
   - 24-hour verification window starts

2. **Donation**
   - Player sends exact verification amount to dev wallet
   - Transaction must be confirmed (6+ blocks)

3. **Automatic Verification**
   - Background service checks every 5 minutes
   - Tries multiple verification methods:
     - ADVC Explorer API
     - Pool Payment History
     - Web Scraping (fallback)

4. **Verification Success**
   - Player marked as verified
   - AP refund calculated (amount × 100)
   - WebSocket notification sent
   - Verification logged

5. **Expiration Handling**
   - After 24 hours, verification challenge expires
   - Player can re-register with new verification amount

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///m2p.db` | Database connection URL |
| `DEV_WALLET_ADDRESS` | **Required** | Developer wallet for donations |
| `VERIFICATION_TIMEOUT_HOURS` | `24` | Verification challenge timeout |
| `VERIFICATION_CHECK_INTERVAL_MINUTES` | `5` | Background check frequency |
| `MIN_CONFIRMATIONS` | `6` | Minimum blockchain confirmations |
| `AP_REFUND_MULTIPLIER` | `100` | AP per ADVC (1 ADVC = 100 AP) |
| `ADMIN_API_KEY` | **Required** | Admin authentication key |
| `SECRET_KEY` | **Required** | Flask secret key |
| `PORT` | `5000` | Server port |

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=server tests/
```

### Manual Verification Testing

```bash
# Start the server
python -m server.app

# Register a player (in another terminal)
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "test_wallet_123"}'

# Manually verify (admin)
curl -X POST http://localhost:5000/admin/verify-player \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_admin_key" \
  -d '{"wallet_address": "test_wallet_123"}'
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions including:
- Systemd service setup
- Nginx reverse proxy configuration
- SSL/TLS setup
- Database migration to PostgreSQL
- Monitoring and logging

## Security Considerations

1. **Always change default keys in production**:
   - `ADMIN_API_KEY`
   - `SECRET_KEY`

2. **Use HTTPS in production** to protect API keys and sensitive data

3. **Database**: Consider PostgreSQL or MySQL for production instead of SQLite

4. **Rate Limiting**: Implement rate limiting on registration endpoint to prevent abuse

5. **Firewall**: Restrict admin endpoints to trusted IPs

## Troubleshooting

### Verification Not Working

1. Check logs: `tail -f logs/verifier.log`
2. Verify API endpoints are accessible:
   ```bash
   curl https://api.adventurecoin.quest/transactions/dev_wallet
   ```
3. Check transaction confirmations on blockchain
4. Verify dev wallet address is correct in `.env`

### Database Issues

```bash
# Reset database
rm m2p.db
python init_db.py
```

### Service Not Starting

```bash
# Check service status
sudo systemctl status m2p-verifier

# View logs
sudo journalctl -u m2p-verifier -f
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: See docs/ directory
- Discord: [Your Discord Server]
