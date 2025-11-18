# Architecture Guide

## Table of Contents
- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [Service Layer](#service-layer)
- [WebSocket Architecture](#websocket-architecture)
- [Security Architecture](#security-architecture)
- [Scalability Design](#scalability-design)

## System Overview

Mine to Play (M2P) is built on a modern, scalable architecture that separates concerns across multiple layers:

```
┌──────────────────────────────────────────────────────────────┐
│                      Presentation Layer                       │
│                    (React + TypeScript)                       │
└───────────────────────────┬──────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  API Gateway   │
                    │  (Nginx + SSL) │
                    └───────┬────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                     Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   REST API   │  │  WebSocket   │  │    Auth      │      │
│  │  (Express)   │  │  (Socket.io) │  │  Middleware  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                      Business Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Pool Service  │  │Achievement   │  │   Player     │      │
│  │              │  │Service       │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Verification  │  │  Reward      │  │ Leaderboard  │      │
│  │Service       │  │  Service     │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                       Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  Blockchain  │      │
│  │   (Primary)  │  │   (Cache)    │  │  (External)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Components

#### 1. Client Application (React + TypeScript)
```
client/
├── src/
│   ├── components/
│   │   ├── common/           # Reusable UI components
│   │   ├── pools/            # Pool-related components
│   │   ├── achievements/     # Achievement displays
│   │   ├── player/           # Player profile components
│   │   └── leaderboard/      # Leaderboard components
│   ├── hooks/
│   │   ├── useWallet.ts      # Wallet connection hook
│   │   ├── useWebSocket.ts   # WebSocket hook
│   │   ├── usePool.ts        # Pool operations hook
│   │   └── useAchievements.ts # Achievement tracking hook
│   ├── services/
│   │   ├── api.ts            # REST API client
│   │   ├── websocket.ts      # WebSocket client
│   │   └── wallet.ts         # Wallet integration
│   ├── store/
│   │   ├── slices/           # Redux slices
│   │   └── index.ts          # Store configuration
│   └── utils/
│       ├── validation.ts     # Input validation
│       └── formatting.ts     # Data formatting
```

**Key Responsibilities:**
- User interface rendering
- Wallet connection management
- Real-time data updates via WebSocket
- Local state management
- API communication

### Backend Components

#### 2. API Server (Express + TypeScript)
```
server/
├── src/
│   ├── controllers/
│   │   ├── authController.ts
│   │   ├── poolController.ts
│   │   ├── achievementController.ts
│   │   └── playerController.ts
│   ├── services/
│   │   ├── poolService.ts
│   │   ├── achievementService.ts
│   │   ├── playerService.ts
│   │   ├── verificationService.ts
│   │   ├── rewardService.ts
│   │   └── leaderboardService.ts
│   ├── middleware/
│   │   ├── auth.ts           # Authentication
│   │   ├── rateLimit.ts      # Rate limiting
│   │   ├── validation.ts     # Input validation
│   │   └── errorHandler.ts   # Error handling
│   ├── routes/
│   │   ├── auth.ts
│   │   ├── pools.ts
│   │   ├── achievements.ts
│   │   └── players.ts
│   └── websocket/
│       ├── handlers/
│       │   ├── poolHandlers.ts
│       │   ├── gameHandlers.ts
│       │   └── chatHandlers.ts
│       └── middleware/
│           └── wsAuth.ts
```

**Key Responsibilities:**
- HTTP request handling
- Business logic execution
- Database operations
- WebSocket connections
- Authentication and authorization

## Data Flow

### Request Flow (REST API)

```
1. Client Request
   │
   ▼
2. Nginx (SSL Termination, Rate Limiting)
   │
   ▼
3. Express Router
   │
   ▼
4. Authentication Middleware
   │
   ▼
5. Validation Middleware
   │
   ▼
6. Controller (Route Handler)
   │
   ▼
7. Service Layer (Business Logic)
   │
   ▼
8. Data Layer (Database/Cache)
   │
   ▼
9. Response Formatting
   │
   ▼
10. Client Response
```

### WebSocket Flow

```
1. Client Connection
   │
   ▼
2. WebSocket Handshake
   │
   ▼
3. Authentication
   │
   ▼
4. Room Assignment (Pool/Game)
   │
   ▼
5. Event Listener Registration
   │
   ▼
6. Bidirectional Communication
   ├─> Client Events → Server Handlers
   └─> Server Events → Client Handlers
```

## Database Schema

### Core Tables

#### Players Table
```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    username VARCHAR(50),
    verification_level INTEGER DEFAULT 0,
    achievement_points INTEGER DEFAULT 0,
    total_rewards DECIMAL(20, 8) DEFAULT 0,
    is_banned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_players_wallet ON players(wallet_address);
CREATE INDEX idx_players_ap ON players(achievement_points DESC);
CREATE INDEX idx_players_active ON players(last_active DESC);
```

#### Pools Table
```sql
CREATE TABLE pools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    difficulty INTEGER NOT NULL,
    max_players INTEGER,
    current_players INTEGER DEFAULT 0,
    total_hashrate BIGINT DEFAULT 0,
    reward_per_block DECIMAL(20, 8),
    fee_percentage DECIMAL(5, 2),
    owner_wallet VARCHAR(42),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config JSONB,
    stats JSONB
);

CREATE INDEX idx_pools_type ON pools(type);
CREATE INDEX idx_pools_active ON pools(is_active);
```

#### Pool Members Table
```sql
CREATE TABLE pool_members (
    id SERIAL PRIMARY KEY,
    pool_id INTEGER REFERENCES pools(id),
    player_id INTEGER REFERENCES players(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hashrate BIGINT DEFAULT 0,
    shares_submitted INTEGER DEFAULT 0,
    rewards_earned DECIMAL(20, 8) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(pool_id, player_id)
);

CREATE INDEX idx_pool_members_pool ON pool_members(pool_id);
CREATE INDEX idx_pool_members_player ON pool_members(player_id);
```

#### Achievements Table
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    tier VARCHAR(20) NOT NULL, -- Bronze, Silver, Gold, Platinum, Diamond
    ap_reward INTEGER NOT NULL,
    icon_url VARCHAR(255),
    requirements JSONB NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_achievements_tier ON achievements(tier);
```

#### Player Achievements Table
```sql
CREATE TABLE player_achievements (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    achievement_id INTEGER REFERENCES achievements(id),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress JSONB,
    UNIQUE(player_id, achievement_id)
);

CREATE INDEX idx_player_achievements_player ON player_achievements(player_id);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    type VARCHAR(50) NOT NULL, -- reward, penalty, transfer
    amount DECIMAL(20, 8) NOT NULL,
    pool_id INTEGER REFERENCES pools(id),
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_player ON transactions(player_id);
CREATE INDEX idx_transactions_created ON transactions(created_at DESC);
```

### Relationships

```
players (1) ──────────── (*) pool_members
   │                           │
   │                           │
   └─ (1) ─────────────── (*) player_achievements
   │                           │
   │                           │
   └─ (1) ─────────────── (*) transactions

pools (1) ──────────────── (*) pool_members

achievements (1) ───────── (*) player_achievements
```

## Service Layer

### Pool Service

**Responsibilities:**
- Pool creation and management
- Player join/leave operations
- Hashrate calculation
- Reward distribution
- Pool statistics

**Key Methods:**
```typescript
class PoolService {
  async createPool(config: PoolConfig): Promise<Pool>
  async joinPool(playerId: number, poolId: number): Promise<void>
  async leavePool(playerId: number, poolId: number): Promise<void>
  async submitShare(playerId: number, poolId: number, share: Share): Promise<void>
  async calculateRewards(poolId: number): Promise<void>
  async getPoolStats(poolId: number): Promise<PoolStats>
}
```

### Achievement Service

**Responsibilities:**
- Achievement tracking
- Progress calculation
- Unlock detection
- AP award distribution

**Key Methods:**
```typescript
class AchievementService {
  async checkAchievements(playerId: number): Promise<Achievement[]>
  async unlockAchievement(playerId: number, achievementId: number): Promise<void>
  async getPlayerAchievements(playerId: number): Promise<PlayerAchievement[]>
  async updateProgress(playerId: number, event: GameEvent): Promise<void>
}
```

### Player Service

**Responsibilities:**
- Player profile management
- Verification handling
- Statistics tracking
- Ban management

**Key Methods:**
```typescript
class PlayerService {
  async getOrCreatePlayer(wallet: string): Promise<Player>
  async updateProfile(playerId: number, data: ProfileData): Promise<Player>
  async verifyPlayer(playerId: number, level: number): Promise<void>
  async banPlayer(playerId: number, reason: string): Promise<void>
  async getPlayerStats(playerId: number): Promise<PlayerStats>
}
```

## WebSocket Architecture

### Connection Management

```typescript
// Server-side connection handler
io.on('connection', (socket) => {
  // Authentication
  const player = await authenticateSocket(socket);

  // Join player room
  socket.join(`player:${player.id}`);

  // Event handlers
  socket.on('join_pool', handleJoinPool);
  socket.on('submit_share', handleSubmitShare);
  socket.on('disconnect', handleDisconnect);
});
```

### Event Categories

1. **Pool Events**
   - `pool_update` - Pool state changes
   - `member_joined` - New member joined
   - `member_left` - Member left
   - `reward_distributed` - Rewards distributed

2. **Achievement Events**
   - `achievement_unlocked` - Achievement earned
   - `progress_update` - Progress changed

3. **Game Events**
   - `hashrate_update` - Hashrate changed
   - `difficulty_adjusted` - Difficulty changed

4. **System Events**
   - `leaderboard_update` - Leaderboard changed
   - `maintenance_notice` - System maintenance

### Room Structure

```
Rooms:
├── global                    # All connected clients
├── player:{id}              # Individual player
├── pool:{id}                # Pool members
└── verified:{level}         # Verified players by level
```

## Security Architecture

### Authentication Flow

```
1. User connects wallet
   │
   ▼
2. Frontend requests challenge
   │
   ▼
3. Backend generates nonce
   │
   ▼
4. User signs nonce with wallet
   │
   ▼
5. Backend verifies signature
   │
   ▼
6. JWT token issued
   │
   ▼
7. Token used for API requests
```

### Security Layers

1. **Transport Security**
   - TLS/SSL encryption
   - HTTPS enforcement
   - Secure WebSocket (WSS)

2. **Authentication**
   - Wallet signature verification
   - JWT token validation
   - Session management

3. **Authorization**
   - Role-based access control
   - Resource ownership verification
   - Action permissions

4. **Input Validation**
   - Schema validation (Joi/Zod)
   - Sanitization
   - Type checking

5. **Rate Limiting**
   - Per-IP limits
   - Per-user limits
   - Endpoint-specific limits

6. **Data Protection**
   - SQL injection prevention (Prisma ORM)
   - XSS protection
   - CSRF tokens
   - Content Security Policy

## Scalability Design

### Horizontal Scaling

```
                     ┌─────────────┐
                     │Load Balancer│
                     └──────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Server 1│         │ Server 2│         │ Server 3│
   └────┬────┘         └────┬────┘         └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Redis Cluster  │
                    │  (Shared State)│
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  PostgreSQL    │
                    │   (Primary)    │
                    └────────────────┘
```

### Caching Strategy

1. **Redis Layers**
   - Session storage
   - Leaderboard cache
   - Pool statistics cache
   - Achievement progress cache

2. **Cache Invalidation**
   - Time-based expiration
   - Event-driven invalidation
   - Manual invalidation

### Database Optimization

1. **Indexing**
   - Primary keys
   - Foreign keys
   - Frequently queried fields
   - Composite indexes

2. **Query Optimization**
   - Prepared statements
   - Query result caching
   - Connection pooling
   - Read replicas

3. **Data Partitioning**
   - Table partitioning by date
   - Sharding by player ID
   - Archive old data

## Monitoring and Observability

### Metrics Collection

```
Application
    │
    ├─> Prometheus (Metrics)
    │   └─> Grafana (Visualization)
    │
    ├─> Winston (Logging)
    │   └─> ELK Stack (Analysis)
    │
    └─> Sentry (Error Tracking)
```

### Key Metrics

1. **Performance**
   - API response time
   - WebSocket latency
   - Database query time
   - Cache hit rate

2. **Business**
   - Active players
   - Pool utilization
   - Achievements unlocked
   - Rewards distributed

3. **System**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────┐
│               CloudFlare CDN                    │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│          Load Balancer (Nginx)                  │
└───────┬──────────────────────────┬──────────────┘
        │                          │
   ┌────▼─────┐              ┌────▼─────┐
   │ Web      │              │ Web      │
   │ Server 1 │              │ Server 2 │
   └────┬─────┘              └────┬─────┘
        │                          │
        └──────────┬───────────────┘
                   │
   ┌───────────────▼──────────────────┐
   │        Redis Cluster             │
   └───────────────┬──────────────────┘
                   │
   ┌───────────────▼──────────────────┐
   │   PostgreSQL Primary             │
   │   + Read Replicas                │
   └──────────────────────────────────┘
```

### Container Architecture

```
docker-compose.yml
├── nginx          (Reverse proxy)
├── app-server-1   (Node.js API)
├── app-server-2   (Node.js API)
├── redis          (Cache)
├── postgres       (Database)
├── prometheus     (Metrics)
└── grafana        (Dashboards)
```

## Future Enhancements

1. **Microservices Migration**
   - Split into smaller services
   - Service mesh (Istio)
   - gRPC communication

2. **Event Sourcing**
   - Event store
   - CQRS pattern
   - Event replay

3. **Multi-Region**
   - Geographic distribution
   - Data replication
   - Latency optimization

4. **Advanced Analytics**
   - Machine learning
   - Predictive analytics
   - Anomaly detection
