# API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [REST API Endpoints](#rest-api-endpoints)
- [WebSocket Events](#websocket-events)
- [Data Models](#data-models)

## Overview

The M2P API is organized around REST principles. It has predictable resource-oriented URLs, accepts JSON-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

**Base URL**: `https://api.m2p.example.com/api/v1`

**API Version**: v1

## Authentication

### Wallet-Based Authentication

M2P uses blockchain wallet signatures for authentication. The authentication flow:

1. **Request Challenge**
```http
POST /api/v1/auth/challenge
Content-Type: application/json

{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

Response:
```json
{
  "challenge": "Sign this message to authenticate: 1234567890",
  "nonce": "1234567890",
  "expires_at": "2025-11-18T12:30:00Z"
}
```

2. **Submit Signature**
```http
POST /api/v1/auth/verify
Content-Type: application/json

{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "signature": "0x...",
  "nonce": "1234567890"
}
```

Response:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "player": {
    "id": 123,
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "username": "Player123",
    "achievement_points": 1500
  }
}
```

### Using JWT Tokens

Include the JWT token in the Authorization header for all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Anonymous**: 100 requests per 15 minutes per IP
- **Authenticated**: 1000 requests per 15 minutes per user
- **WebSocket**: 100 messages per minute per connection

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1637251200
```

When rate limited, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 300
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error context"
    }
  }
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `409 Conflict` - Request conflicts with current state
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_WALLET` | Invalid wallet address format |
| `SIGNATURE_INVALID` | Signature verification failed |
| `TOKEN_EXPIRED` | JWT token has expired |
| `POOL_FULL` | Pool has reached maximum capacity |
| `INSUFFICIENT_AP` | Not enough achievement points |
| `ALREADY_MEMBER` | Already a member of this pool |
| `PLAYER_BANNED` | Player account is banned |
| `ACHIEVEMENT_LOCKED` | Achievement requirements not met |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

## REST API Endpoints

### Authentication

#### POST /auth/challenge
Request a challenge for wallet authentication.

**Request:**
```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
}
```

**Response: 200 OK**
```json
{
  "challenge": "Sign this message to authenticate: 1234567890",
  "nonce": "1234567890",
  "expires_at": "2025-11-18T12:30:00Z"
}
```

#### POST /auth/verify
Verify wallet signature and obtain JWT token.

**Request:**
```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "signature": "0x...",
  "nonce": "1234567890"
}
```

**Response: 200 OK**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "player": {
    "id": 123,
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "username": "Player123",
    "achievement_points": 1500,
    "verification_level": 2
  }
}
```

#### POST /auth/refresh
Refresh an expired JWT token.

**Headers:**
```
Authorization: Bearer {expired_token}
```

**Response: 200 OK**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### Players

#### GET /players/:wallet
Get player profile by wallet address.

**Response: 200 OK**
```json
{
  "id": 123,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "username": "Player123",
  "achievement_points": 1500,
  "verification_level": 2,
  "total_rewards": "123.456",
  "pools": [
    {
      "id": 1,
      "name": "Elite Miners",
      "joined_at": "2025-11-01T10:00:00Z"
    }
  ],
  "achievements_unlocked": 15,
  "leaderboard_rank": 42,
  "created_at": "2025-10-01T00:00:00Z",
  "last_active": "2025-11-18T10:30:00Z"
}
```

#### PATCH /players/me
Update current player's profile.

**Request:**
```json
{
  "username": "NewUsername",
  "avatar_url": "https://example.com/avatar.png"
}
```

**Response: 200 OK**
```json
{
  "id": 123,
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "username": "NewUsername",
  "avatar_url": "https://example.com/avatar.png",
  "achievement_points": 1500
}
```

#### GET /players/me/stats
Get detailed statistics for current player.

**Response: 200 OK**
```json
{
  "total_hashrate": 1234567890,
  "total_shares": 5000,
  "total_rewards": "123.456",
  "pools_joined": 3,
  "achievements_unlocked": 15,
  "achievement_points": 1500,
  "daily_stats": {
    "hashrate": 123456,
    "shares": 500,
    "rewards": "12.34"
  },
  "weekly_stats": {
    "hashrate": 864000,
    "shares": 3500,
    "rewards": "86.45"
  }
}
```

### Pools

#### GET /pools
List all available pools.

**Query Parameters:**
- `type` (optional) - Filter by pool type
- `active` (optional) - Filter by active status (true/false)
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 20, max: 100) - Items per page

**Response: 200 OK**
```json
{
  "pools": [
    {
      "id": 1,
      "name": "Elite Miners",
      "type": "standard",
      "difficulty": 1000,
      "max_players": 100,
      "current_players": 45,
      "total_hashrate": 987654321,
      "reward_per_block": "50.0",
      "fee_percentage": "2.5",
      "is_active": true,
      "created_at": "2025-10-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "total_pages": 3
  }
}
```

#### GET /pools/:id
Get detailed pool information.

**Response: 200 OK**
```json
{
  "id": 1,
  "name": "Elite Miners",
  "type": "standard",
  "difficulty": 1000,
  "max_players": 100,
  "current_players": 45,
  "total_hashrate": 987654321,
  "reward_per_block": "50.0",
  "fee_percentage": "2.5",
  "owner_wallet": "0x123...",
  "is_active": true,
  "stats": {
    "total_blocks": 1000,
    "total_rewards": "50000.0",
    "avg_hashrate_24h": 950000000,
    "efficiency": 95.5
  },
  "top_members": [
    {
      "player_id": 456,
      "username": "TopMiner",
      "hashrate": 123456789,
      "contribution": 12.5
    }
  ],
  "created_at": "2025-10-01T00:00:00Z"
}
```

#### POST /pools/:id/join
Join a pool.

**Response: 200 OK**
```json
{
  "success": true,
  "pool_id": 1,
  "joined_at": "2025-11-18T10:30:00Z",
  "message": "Successfully joined Elite Miners"
}
```

**Error: 409 Conflict**
```json
{
  "error": {
    "code": "ALREADY_MEMBER",
    "message": "You are already a member of this pool"
  }
}
```

#### POST /pools/:id/leave
Leave a pool.

**Response: 200 OK**
```json
{
  "success": true,
  "rewards_pending": "12.345",
  "message": "Successfully left pool. Rewards will be distributed shortly."
}
```

#### POST /pools/:id/submit-share
Submit a mining share to the pool.

**Request:**
```json
{
  "nonce": "123456",
  "hash": "0x...",
  "difficulty": 1000
}
```

**Response: 200 OK**
```json
{
  "accepted": true,
  "shares_total": 501,
  "hashrate_updated": 123456789
}
```

#### GET /pools/:id/members
Get pool members list.

**Response: 200 OK**
```json
{
  "members": [
    {
      "player_id": 123,
      "username": "Player123",
      "hashrate": 123456789,
      "shares_submitted": 500,
      "contribution": 12.5,
      "joined_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total_members": 45
}
```

### Achievements

#### GET /achievements
List all achievements.

**Query Parameters:**
- `tier` (optional) - Filter by tier (Bronze, Silver, Gold, Platinum, Diamond)
- `unlocked` (optional) - Filter by unlock status for current player

**Response: 200 OK**
```json
{
  "achievements": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Join your first pool",
      "tier": "Bronze",
      "ap_reward": 10,
      "icon_url": "https://example.com/icons/first-steps.png",
      "requirements": {
        "pools_joined": 1
      },
      "unlocked": true,
      "unlocked_at": "2025-11-01T10:05:00Z"
    },
    {
      "id": 2,
      "name": "Hash Master",
      "description": "Reach 1M total hashrate",
      "tier": "Gold",
      "ap_reward": 100,
      "icon_url": "https://example.com/icons/hash-master.png",
      "requirements": {
        "total_hashrate": 1000000
      },
      "unlocked": false,
      "progress": {
        "current": 456789,
        "required": 1000000,
        "percentage": 45.6
      }
    }
  ]
}
```

#### GET /achievements/:id
Get achievement details.

**Response: 200 OK**
```json
{
  "id": 1,
  "name": "First Steps",
  "description": "Join your first pool",
  "tier": "Bronze",
  "ap_reward": 10,
  "icon_url": "https://example.com/icons/first-steps.png",
  "requirements": {
    "pools_joined": 1
  },
  "total_unlocks": 1234,
  "rarity": 12.5,
  "created_at": "2025-10-01T00:00:00Z"
}
```

#### GET /players/me/achievements
Get current player's achievements with progress.

**Response: 200 OK**
```json
{
  "unlocked": [
    {
      "achievement_id": 1,
      "name": "First Steps",
      "tier": "Bronze",
      "ap_reward": 10,
      "unlocked_at": "2025-11-01T10:05:00Z"
    }
  ],
  "in_progress": [
    {
      "achievement_id": 2,
      "name": "Hash Master",
      "tier": "Gold",
      "ap_reward": 100,
      "progress": {
        "current": 456789,
        "required": 1000000,
        "percentage": 45.6
      }
    }
  ],
  "total_ap_earned": 150,
  "total_unlocked": 15
}
```

### Leaderboard

#### GET /leaderboard
Get global leaderboard.

**Query Parameters:**
- `type` (optional, default: 'ap') - Leaderboard type: 'ap', 'hashrate', 'rewards'
- `period` (optional, default: 'all-time') - Time period: 'daily', 'weekly', 'monthly', 'all-time'
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 100, max: 100) - Items per page

**Response: 200 OK**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "player_id": 456,
      "username": "TopPlayer",
      "wallet_address": "0x456...",
      "score": 5000,
      "change": 2
    },
    {
      "rank": 2,
      "player_id": 789,
      "username": "SecondPlace",
      "wallet_address": "0x789...",
      "score": 4500,
      "change": -1
    }
  ],
  "current_player": {
    "rank": 42,
    "score": 1500
  },
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 10000
  }
}
```

### Verification

#### POST /verification/request
Request player verification.

**Request:**
```json
{
  "level": 1,
  "proof": {
    "document_type": "id",
    "document_url": "https://example.com/id.jpg"
  }
}
```

**Response: 200 OK**
```json
{
  "verification_id": "ver_123456",
  "status": "pending",
  "submitted_at": "2025-11-18T10:30:00Z",
  "estimated_review_time": "24 hours"
}
```

#### GET /verification/status
Check verification status.

**Response: 200 OK**
```json
{
  "status": "approved",
  "level": 1,
  "approved_at": "2025-11-18T12:00:00Z"
}
```

## WebSocket Events

Connect to WebSocket server: `wss://api.m2p.example.com`

### Connection

```javascript
import io from 'socket.io-client';

const socket = io('wss://api.m2p.example.com', {
  auth: {
    token: 'your-jwt-token'
  }
});

socket.on('connect', () => {
  console.log('Connected to M2P WebSocket');
});
```

### Client Events (Emit)

#### join_pool
Join a pool room for real-time updates.

```javascript
socket.emit('join_pool', {
  pool_id: 1
});
```

#### leave_pool
Leave a pool room.

```javascript
socket.emit('leave_pool', {
  pool_id: 1
});
```

#### submit_share
Submit a mining share.

```javascript
socket.emit('submit_share', {
  pool_id: 1,
  nonce: '123456',
  hash: '0x...',
  difficulty: 1000
});
```

#### request_stats
Request statistics update.

```javascript
socket.emit('request_stats', {
  type: 'pool',
  id: 1
});
```

### Server Events (Listen)

#### pool_update
Pool state has changed.

```javascript
socket.on('pool_update', (data) => {
  console.log('Pool updated:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "current_players": 46,
  "total_hashrate": 1000000000,
  "difficulty": 1050,
  "timestamp": "2025-11-18T10:30:00Z"
}
```

#### share_accepted
Mining share was accepted.

```javascript
socket.on('share_accepted', (data) => {
  console.log('Share accepted:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "shares_total": 501,
  "hashrate": 123456789
}
```

#### share_rejected
Mining share was rejected.

```javascript
socket.on('share_rejected', (data) => {
  console.log('Share rejected:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "reason": "Invalid difficulty",
  "details": "..."
}
```

#### achievement_unlocked
Achievement was unlocked.

```javascript
socket.on('achievement_unlocked', (data) => {
  console.log('Achievement unlocked:', data);
});
```

**Data:**
```json
{
  "achievement_id": 5,
  "name": "Power Miner",
  "tier": "Gold",
  "ap_reward": 100,
  "total_ap": 1600
}
```

#### reward_distributed
Rewards were distributed.

```javascript
socket.on('reward_distributed', (data) => {
  console.log('Rewards distributed:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "amount": "12.345",
  "shares": 500,
  "timestamp": "2025-11-18T10:30:00Z"
}
```

#### leaderboard_update
Leaderboard has changed.

```javascript
socket.on('leaderboard_update', (data) => {
  console.log('Leaderboard updated:', data);
});
```

**Data:**
```json
{
  "type": "ap",
  "top_players": [
    {
      "rank": 1,
      "username": "TopPlayer",
      "score": 5000
    }
  ],
  "your_rank": 42
}
```

#### member_joined
New member joined pool.

```javascript
socket.on('member_joined', (data) => {
  console.log('Member joined:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "player_id": 999,
  "username": "NewPlayer",
  "current_players": 46
}
```

#### member_left
Member left pool.

```javascript
socket.on('member_left', (data) => {
  console.log('Member left:', data);
});
```

**Data:**
```json
{
  "pool_id": 1,
  "player_id": 999,
  "username": "ExPlayer",
  "current_players": 45
}
```

#### error
Error occurred.

```javascript
socket.on('error', (data) => {
  console.error('WebSocket error:', data);
});
```

**Data:**
```json
{
  "code": "POOL_FULL",
  "message": "Cannot join pool. Maximum capacity reached.",
  "details": {}
}
```

## Data Models

### Player
```typescript
interface Player {
  id: number;
  wallet_address: string;
  username?: string;
  verification_level: number;
  achievement_points: number;
  total_rewards: string;
  is_banned: boolean;
  created_at: string;
  last_active: string;
}
```

### Pool
```typescript
interface Pool {
  id: number;
  name: string;
  type: string;
  difficulty: number;
  max_players: number;
  current_players: number;
  total_hashrate: number;
  reward_per_block: string;
  fee_percentage: string;
  is_active: boolean;
  created_at: string;
}
```

### Achievement
```typescript
interface Achievement {
  id: number;
  name: string;
  description: string;
  tier: 'Bronze' | 'Silver' | 'Gold' | 'Platinum' | 'Diamond';
  ap_reward: number;
  icon_url: string;
  requirements: Record<string, any>;
  is_hidden: boolean;
}
```

### PlayerAchievement
```typescript
interface PlayerAchievement {
  id: number;
  player_id: number;
  achievement_id: number;
  unlocked_at: string;
  progress?: {
    current: number;
    required: number;
    percentage: number;
  };
}
```

## Webhooks

M2P can send webhooks for important events (configured per account):

### Webhook Events

- `player.verified` - Player verification completed
- `achievement.unlocked` - Player unlocked achievement
- `pool.created` - New pool created
- `reward.distributed` - Rewards distributed

### Webhook Payload

```json
{
  "event": "achievement.unlocked",
  "timestamp": "2025-11-18T10:30:00Z",
  "data": {
    "player_id": 123,
    "achievement_id": 5,
    "ap_reward": 100
  }
}
```

### Webhook Signature

Webhooks include a signature header for verification:

```
X-M2P-Signature: sha256=...
```

Verify using your webhook secret:
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
}
```

## SDKs and Client Libraries

Official SDKs:
- **JavaScript/TypeScript**: `@m2p/sdk`
- **Python**: `m2p-sdk`

Example usage:
```javascript
import { M2PClient } from '@m2p/sdk';

const client = new M2PClient({
  apiKey: 'your-jwt-token'
});

const player = await client.players.get('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb');
const pools = await client.pools.list();
```

## Changelog

### v1.0.0 (2025-11-18)
- Initial API release
- Core endpoints for players, pools, achievements
- WebSocket real-time updates
- Wallet-based authentication
