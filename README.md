# M2P - Mining to Play

A Flask-based API server with WebSocket support for a blockchain gaming reward system built on Advancecoin (ADVC).

## Overview

M2P (Mining to Play) is a gamification layer for cryptocurrency mining that rewards miners with Action Points (AP) which can be spent on in-game items, upgrades, and features. The system tracks mining events, manages player achievements, and provides real-time notifications via WebSocket.

## Features

- **Player Registration & Verification**: Wallet-based registration with verification challenge
- **Mining Reward Tracking**: Automatic tracking of mining events and AP rewards
- **Achievement System**: Unlock achievements and earn bonus AP
- **Leaderboard**: Global and time-based rankings (all-time, weekly, daily)
- **AP Economy**: Spend AP on items and upgrades
- **Real-time Notifications**: WebSocket support for instant updates
- **RESTful API**: Comprehensive API for all operations
- **Rate Limiting**: Built-in protection against abuse
- **Database Support**: SQLite (dev) and PostgreSQL (production)

## Project Structure

```
m2p/
├── server/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── run.sh              # Startup script
│   └── .env.example        # Environment configuration template
├── requirements.txt        # Python dependencies
├── API_DOCUMENTATION.md    # Complete API documentation
├── .gitignore
└── README.md
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd m2p

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp server/.env.example server/.env

# Edit .env with your settings
nano server/.env
```

Required configuration:
- `SECRET_KEY`: Random secret key for Flask
- `DATABASE_URL`: Database connection string
- `DONATION_ADDRESS`: Your Advancecoin donation address

### 3. Initialize Database

```bash
cd server
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4. Run Server

**Development Mode:**
```bash
cd server
python app.py
```

**Production Mode:**
```bash
cd server
./run.sh
```

The server will start on `http://localhost:5000`

## API Endpoints

### Player Management
- `POST /api/register` - Register new player
- `GET /api/player/:wallet` - Get player info
- `POST /api/player/:wallet/verify` - Verify wallet ownership
- `POST /api/player/:wallet/spend-ap` - Spend Action Points

### Leaderboard
- `GET /api/leaderboard` - Get top players
- `GET /api/leaderboard/:wallet/rank` - Get player rank

### Achievements
- `GET /api/achievements` - List all achievements
- `GET /api/player/:wallet/achievements` - Get player's achievements

### Statistics
- `GET /api/stats` - Global statistics

### Health
- `GET /health` - Server health check

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## WebSocket Events

### Client → Server
- `connect` - Initial connection
- `join` - Join wallet-specific room
- `leave` - Leave room
- `ping` - Heartbeat

### Server → Client
- `mining_reward` - New mining reward received
- `verification_complete` - Wallet verification successful
- `achievement_unlocked` - Achievement earned
- `rank_changed` - Leaderboard rank updated

## Database Schema

### Tables
- **players**: Player accounts and stats
- **mining_events**: Mining reward history
- **achievements**: Available achievements
- **player_achievements**: Unlocked achievements
- **purchases**: AP spending history

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

### Code Style

```bash
# Install formatting tools
pip install black flake8

# Format code
black server/

# Check style
flake8 server/
```

## Production Deployment

### Using Gunicorn + Nginx

1. Install Gunicorn:
```bash
pip install gunicorn eventlet
```

2. Run with Gunicorn:
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 server.app:app
```

3. Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/

WORKDIR /app/server

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Configure proper CORS origins
- Use PostgreSQL instead of SQLite
- Implement proper transaction verification
- Add authentication for sensitive endpoints
- Monitor rate limits
- Regular security audits

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key...` |
| `DATABASE_URL` | Database connection | `sqlite:///m2p.db` |
| `DONATION_ADDRESS` | ADVC donation address | Required |
| `FLASK_HOST` | Server host | `0.0.0.0` |
| `FLASK_PORT` | Server port | `5000` |
| `FLASK_DEBUG` | Debug mode | `False` |

## Troubleshooting

### Database Connection Errors
- Verify `DATABASE_URL` in `.env`
- Ensure database exists and is accessible
- Check user permissions

### WebSocket Connection Failed
- Verify CORS settings in `app.py`
- Check firewall rules
- Ensure client uses correct protocol (ws:// or wss://)

### Rate Limit Exceeded
- Adjust limits in `app.py`
- Consider using Redis for distributed rate limiting

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Implement blockchain transaction verification
- [ ] Add OAuth2 authentication
- [ ] Create admin dashboard
- [ ] Add more achievement types
- [ ] Implement quest system
- [ ] Add item marketplace
- [ ] Mobile app support
- [ ] Multi-language support

## Acknowledgments

- Built with Flask and Flask-SocketIO
- Designed for Advancecoin (ADVC) blockchain
- Inspired by play-to-earn gaming models