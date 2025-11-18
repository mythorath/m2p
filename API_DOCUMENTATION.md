# M2P Flask API Documentation

Complete API documentation for the Mining to Play (M2P) Flask server with WebSocket support.

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [REST API Endpoints](#rest-api-endpoints)
- [WebSocket Events](#websocket-events)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

**Base URL**: `http://localhost:5000`
**WebSocket URL**: `ws://localhost:5000`

All REST API endpoints return JSON responses.
All timestamps are in ISO 8601 format (UTC).

---

## Authentication

Currently, the API does not require authentication tokens. Players are identified by their wallet addresses.

---

## REST API Endpoints

### Health Check

**GET** `/health`

Check server and database status.

**Response** (200):
```json
{
  "status": "ok",
  "database": "connected",
  "timestamp": "2025-11-18T12:00:00"
}
```

---

### Player Management

#### Register New Player

**POST** `/api/register`

Register a new player and receive verification challenge.

**Request Body**:
```json
{
  "wallet_address": "A1234567890123456789012345678901234",
  "display_name": "PlayerOne"
}
```

**Validation**:
- `wallet_address`: Must start with 'A', 34 characters total
- `display_name`: 3-50 characters

**Response** (201):
```json
{
  "challenge_amount": 1.5234,
  "donation_address": "ASYSTEM_DONATION_ADDRESS_HERE",
  "expires_at": "2025-11-19T12:00:00"
}
```

**Errors**:
- `400`: Invalid input or validation failed
- `409`: Player already registered

**Rate Limit**: 5 requests per hour

---

#### Get Player Info

**GET** `/api/player/:wallet`

Retrieve player statistics and recent activity.

**Parameters**:
- `wallet`: Player wallet address (path parameter)

**Response** (200):
```json
{
  "wallet_address": "A1234567890123456789012345678901234",
  "display_name": "PlayerOne",
  "verified": true,
  "total_ap": 1000,
  "spent_ap": 200,
  "available_ap": 800,
  "total_mined_advc": 123.456789,
  "created_at": "2025-11-01T00:00:00",
  "recent_events": [
    {
      "id": 1,
      "amount_advc": 10.5,
      "ap_awarded": 105,
      "pool": "pool.example.com",
      "timestamp": "2025-11-18T10:30:00"
    }
  ],
  "achievements_unlocked": 5
}
```

**Errors**:
- `400`: Invalid wallet address format
- `404`: Player not found

---

#### Verify Player Wallet

**POST** `/api/player/:wallet/verify`

Verify wallet ownership via transaction.

**Parameters**:
- `wallet`: Player wallet address (path parameter)

**Request Body**:
```json
{
  "tx_hash": "transaction_hash_here"
}
```

**Response** (200):
```json
{
  "verified": true,
  "ap_credited": 152
}
```

**Side Effects**:
- Emits `verification_complete` WebSocket event to player's room

**Errors**:
- `400`: Invalid input, already verified, or challenge expired
- `404`: Player not found

**Rate Limit**: 10 requests per hour

---

#### Spend Action Points

**POST** `/api/player/:wallet/spend-ap`

Spend AP on items or upgrades.

**Parameters**:
- `wallet`: Player wallet address (path parameter)

**Request Body**:
```json
{
  "amount": 100,
  "item_id": "power_boost_001",
  "item_name": "Power Boost"
}
```

**Response** (200):
```json
{
  "new_balance": 700,
  "spent": 100
}
```

**Errors**:
- `400`: Invalid input, negative amount, or insufficient balance
- `404`: Player not found

**Rate Limit**: 20 requests per hour

---

### Leaderboard

#### Get Leaderboard

**GET** `/api/leaderboard`

Retrieve top players by mining performance.

**Query Parameters**:
- `period`: `all_time` (default), `week`, or `day`
- `limit`: Number of results (default: 50, max: 100)

**Example**: `/api/leaderboard?period=week&limit=10`

**Response** (200):
```json
[
  {
    "rank": 1,
    "wallet_address": "A1234567890123456789012345678901234",
    "display_name": "TopMiner",
    "total_mined_advc": 9999.12345678,
    "total_ap": 999912
  },
  {
    "rank": 2,
    "wallet_address": "A9876543210987654321098765432109876",
    "display_name": "SecondPlace",
    "total_mined_advc": 8888.87654321,
    "total_ap": 888887
  }
]
```

**Errors**:
- `400`: Invalid limit parameter

---

#### Get Player Rank

**GET** `/api/leaderboard/:wallet/rank`

Get specific player's rank on leaderboard.

**Parameters**:
- `wallet`: Player wallet address (path parameter)

**Response** (200):
```json
{
  "rank": 42,
  "total_mined_advc": 123.456789,
  "total_players": 1000
}
```

**Errors**:
- `400`: Invalid wallet address format
- `404`: Player not found

---

### Achievements

#### Get All Achievements

**GET** `/api/achievements`

List all available achievements.

**Query Parameters** (optional):
- `wallet`: Include unlock status for specific player

**Response** (200):
```json
[
  {
    "id": 1,
    "name": "First Mine",
    "description": "Complete your first mining event",
    "ap_reward": 100,
    "icon": "trophy",
    "unlocked": true,
    "unlocked_at": "2025-11-01T12:00:00"
  },
  {
    "id": 2,
    "name": "Century Club",
    "description": "Mine 100 ADVC total",
    "ap_reward": 500,
    "icon": "star",
    "unlocked": false
  }
]
```

**Errors**:
- `400`: Invalid wallet address format (if provided)

---

#### Get Player Achievements

**GET** `/api/player/:wallet/achievements`

Get player's unlocked achievements.

**Parameters**:
- `wallet`: Player wallet address (path parameter)

**Response** (200):
```json
[
  {
    "achievement_id": 1,
    "achievement_name": "First Mine",
    "achievement_description": "Complete your first mining event",
    "ap_reward": 100,
    "icon": "trophy",
    "unlocked_at": "2025-11-01T12:00:00"
  }
]
```

**Errors**:
- `400`: Invalid wallet address format
- `404`: Player not found

---

### Statistics

#### Get Global Stats

**GET** `/api/stats`

Retrieve global system statistics.

**Response** (200):
```json
{
  "total_players": 1000,
  "verified_players": 850,
  "total_advc_mined": 123456.789,
  "total_ap_awarded": 12345678,
  "total_mining_events": 50000
}
```

---

## WebSocket Events

### Client → Server

#### Connect
Automatic event when client connects.

**Server Response**:
```json
{
  "status": "connected",
  "message": "Successfully connected to M2P server",
  "timestamp": "2025-11-18T12:00:00"
}
```

---

#### Join Room

**Event**: `join`

Join wallet-specific room for notifications.

**Payload**:
```json
{
  "wallet": "A1234567890123456789012345678901234"
}
```

**Response**:
```json
{
  "status": "joined",
  "wallet": "A1234567890123456789012345678901234",
  "message": "Joined notification room for A1234..."
}
```

---

#### Leave Room

**Event**: `leave`

Leave wallet-specific room.

**Payload**:
```json
{
  "wallet": "A1234567890123456789012345678901234"
}
```

**Response**:
```json
{
  "status": "left",
  "wallet": "A1234567890123456789012345678901234",
  "message": "Left notification room for A1234..."
}
```

---

#### Ping (Heartbeat)

**Event**: `ping`

**Response** (`pong`):
```json
{
  "timestamp": "2025-11-18T12:00:00"
}
```

---

### Server → Client

#### Mining Reward

**Event**: `mining_reward`

Emitted when player receives mining reward.

**Payload**:
```json
{
  "amount_advc": 10.5,
  "ap_awarded": 105,
  "pool": "pool.example.com",
  "timestamp": "2025-11-18T12:00:00"
}
```

---

#### Verification Complete

**Event**: `verification_complete`

Emitted when wallet verification succeeds.

**Payload**:
```json
{
  "ap_refunded": 152
}
```

---

#### Achievement Unlocked

**Event**: `achievement_unlocked`

Emitted when player unlocks achievement.

**Payload**:
```json
{
  "achievement_id": 1,
  "name": "First Mine",
  "ap_reward": 100,
  "timestamp": "2025-11-18T12:00:00"
}
```

---

#### Rank Changed

**Event**: `rank_changed`

Emitted when player's leaderboard rank changes.

**Payload**:
```json
{
  "new_rank": 42,
  "old_rank": 45,
  "timestamp": "2025-11-18T12:00:00"
}
```

---

## Error Handling

All errors return JSON with the following format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `409`: Conflict (e.g., already exists)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

---

## Rate Limiting

Default limits:
- **Global**: 200 requests/day, 50 requests/hour
- **Registration**: 5 requests/hour
- **Verification**: 10 requests/hour
- **Spend AP**: 20 requests/hour

Rate limit headers:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Example Client Usage

### Python (REST API)

```python
import requests

# Register player
response = requests.post('http://localhost:5000/api/register', json={
    'wallet_address': 'A1234567890123456789012345678901234',
    'display_name': 'PlayerOne'
})
print(response.json())

# Get player info
response = requests.get('http://localhost:5000/api/player/A1234567890123456789012345678901234')
print(response.json())
```

### JavaScript (WebSocket)

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected');

  // Join wallet room
  socket.emit('join', {
    wallet: 'A1234567890123456789012345678901234'
  });
});

socket.on('mining_reward', (data) => {
  console.log('Mining reward received:', data);
});

socket.on('achievement_unlocked', (data) => {
  console.log('Achievement unlocked:', data);
});
```

---

## Production Deployment

### Environment Variables

Set the following in production:

```bash
export SECRET_KEY="your-random-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/m2p"
export DONATION_ADDRESS="your-advc-donation-address"
export FLASK_DEBUG=False
```

### Run with Gunicorn

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 server.app:app
```

### Database Migration

```bash
cd server
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## Support

For issues or questions, please contact the development team or submit an issue on the project repository.
