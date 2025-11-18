# M2P Wallet Verification System - Quick Start Guide

Get the M2P Wallet Verification System up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd m2p
```

### 2. Run Setup Script

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Copy `.env.example` to `.env`
- Create logs directory

### 3. Configure Environment

Edit `.env` file and set **required** values:

```bash
nano .env
```

**Required settings:**
```bash
DEV_WALLET_ADDRESS=your_actual_advc_wallet_address
ADMIN_API_KEY=generate_a_secure_random_key
SECRET_KEY=generate_a_secure_random_key
```

**Generate secure keys:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Initialize Database

```bash
source venv/bin/activate
python init_db.py
```

Type `yes` when prompted to create tables.

### 5. Start the Server

```bash
python -m server.app
```

You should see:
```
Starting M2P server on port 5000
```

## Test the System

### Option 1: Interactive Test

In a new terminal:

```bash
source venv/bin/activate
python test_example.py
```

Follow the interactive menu to test all features.

### Option 2: Automated Test

```bash
python test_example.py auto
```

This runs a complete automated test flow.

### Option 3: Manual cURL Tests

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Register Player:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "ADVC_test_wallet_123"}'
```

**Get Player Info:**
```bash
curl http://localhost:5000/api/player/ADVC_test_wallet_123
```

**Admin: Manually Verify Player:**
```bash
curl -X POST http://localhost:5000/admin/verify-player \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_admin_api_key" \
  -d '{"wallet_address": "ADVC_test_wallet_123"}'
```

## How It Works

### 1. Player Registration
Player provides wallet address → System generates random verification amount (0.1-1.0 ADVC)

### 2. Donation
Player sends exact amount to dev wallet → Has 24 hours to complete

### 3. Verification
- Background service checks every 5 minutes
- Tries 3 verification methods:
  1. ADVC Explorer API
  2. Pool Payment History
  3. Web Scraping (fallback)

### 4. Success
- Player marked as verified
- AP credited (amount × 100)
- Real-time notification sent

## What's Next?

### For Development

1. **Read the full documentation:**
   - [README.md](README.md) - Complete overview
   - [API.md](API.md) - API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup

2. **Explore the code:**
   - `server/models.py` - Database models
   - `server/verifier.py` - Verification logic
   - `server/app.py` - API endpoints
   - `server/config.py` - Configuration

3. **Run tests:**
   ```bash
   python test_example.py
   ```

### For Production

1. **Switch to PostgreSQL:**
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost/m2p
   ```

2. **Install as systemd service:**
   ```bash
   sudo cp m2p-verifier.service /etc/systemd/system/
   sudo systemctl enable m2p-verifier
   sudo systemctl start m2p-verifier
   ```

3. **Set up Nginx reverse proxy** (see DEPLOYMENT.md)

4. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Common Issues

### Port Already in Use
```bash
# Change port in .env
PORT=5001
```

### Database Errors
```bash
# Reset database
rm m2p.db
python init_db.py
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Verification Not Working
```bash
# Check dev wallet address is correct
grep DEV_WALLET_ADDRESS .env

# View logs
tail -f logs/verifier.log
```

## API Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/register` | POST | No | Register player |
| `/api/player/:wallet` | GET | No | Get player info |
| `/api/verify-now` | POST | No | Check verification |
| `/admin/verify-player` | POST | Yes | Manual verify |
| `/admin/players` | GET | Yes | List players |
| `/admin/verification-logs` | GET | Yes | View logs |

## WebSocket Events

**Join room:**
```javascript
socket.emit('join', { wallet_address: 'your_wallet' });
```

**Listen for verification:**
```javascript
socket.on('verification_complete', (data) => {
  console.log('Verified!', data.ap_credited, 'AP');
});
```

## Architecture

```
┌─────────────┐
│   Player    │
│  Frontend   │
└──────┬──────┘
       │
       │ HTTP/WebSocket
       ▼
┌─────────────────────────────────┐
│      Flask Application          │
│  ┌──────────┐  ┌─────────────┐ │
│  │   API    │  │  WebSocket  │ │
│  │ Endpoints│  │  Notifications│ │
│  └────┬─────┘  └──────┬──────┘ │
│       │               │         │
│  ┌────┴───────────────┴──────┐ │
│  │   Wallet Verifier         │ │
│  │  ┌────────────────────┐   │ │
│  │  │ Background Loop    │   │ │
│  │  │ (Every 5 minutes)  │   │ │
│  │  └─────────┬──────────┘   │ │
│  └────────────┼──────────────┘ │
└───────────────┼────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌─────────┐
│Explorer│ │  Pool  │ │   Web   │
│  API   │ │  API   │ │Scraping │
└────────┘ └────────┘ └─────────┘
    │           │           │
    └───────────┴───────────┘
                │
                ▼
        ┌───────────────┐
        │  Blockchain   │
        │ (ADVC Network)│
        └───────────────┘
```

## Support

- **Documentation:** See [README.md](README.md) for detailed docs
- **API Reference:** See [API.md](API.md)
- **Deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues:** Report bugs on GitHub

## License

MIT License - See LICENSE file

---

**Ready to go!** Start the server and test with `python test_example.py`
