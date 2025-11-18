# Performance Optimization Guide

## Database Optimization

### Indexing Strategy

```sql
-- Critical indexes for M2P

-- Players table
CREATE INDEX CONCURRENTLY idx_players_wallet ON players(wallet_address);
CREATE INDEX CONCURRENTLY idx_players_ap ON players(achievement_points DESC);
CREATE INDEX CONCURRENTLY idx_players_last_active ON players(last_active DESC);

-- Pools table
CREATE INDEX CONCURRENTLY idx_pools_type_active ON pools(type, is_active);
CREATE INDEX CONCURRENTLY idx_pools_current_players ON pools(current_players);

-- Pool members table
CREATE INDEX CONCURRENTLY idx_pool_members_pool ON pool_members(pool_id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_pool_members_player ON pool_members(player_id);
CREATE INDEX CONCURRENTLY idx_pool_members_composite ON pool_members(pool_id, player_id);

-- Achievements table
CREATE INDEX CONCURRENTLY idx_player_achievements_player ON player_achievements(player_id);
CREATE INDEX CONCURRENTLY idx_player_achievements_unlocked ON player_achievements(unlocked_at DESC);

-- Transactions table
CREATE INDEX CONCURRENTLY idx_transactions_player_created ON transactions(player_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_transactions_type ON transactions(type);
```

### Query Optimization

```typescript
// BAD: N+1 query problem
const pools = await prisma.pool.findMany();
for (const pool of pools) {
  const members = await prisma.poolMember.findMany({
    where: { poolId: pool.id }
  });
}

// GOOD: Use include to join
const pools = await prisma.pool.findMany({
  include: {
    members: {
      where: { isActive: true }
    }
  }
});

// GOOD: Use select to limit fields
const players = await prisma.player.findMany({
  select: {
    id: true,
    walletAddress: true,
    achievementPoints: true,
    // Don't select unused fields
  }
});
```

### Connection Pooling

```typescript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  // Connection pool settings
  pool_size = 20
  connection_limit = 20
  pool_timeout = 30
}
```

### Database Maintenance

```sql
-- Regular maintenance tasks

-- Vacuum and analyze (weekly)
VACUUM ANALYZE;

-- Reindex (monthly)
REINDEX DATABASE m2p_db;

-- Update planner statistics
ANALYZE players;
ANALYZE pools;
ANALYZE pool_members;

-- Check for bloat
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Caching Strategy

### Redis Caching

```typescript
import Redis from 'ioredis';

const redis = new Redis({
  host: 'localhost',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  db: 0,
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  // Connection pool
  lazyConnect: false,
  connectionName: 'm2p-api',
});

// Cache wrapper
async function cached<T>(
  key: string,
  fn: () => Promise<T>,
  ttl: number = 300
): Promise<T> {
  // Try to get from cache
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }

  // Execute function and cache result
  const result = await fn();
  await redis.setex(key, ttl, JSON.stringify(result));

  return result;
}

// Usage
const pools = await cached('pools:active', async () => {
  return await prisma.pool.findMany({ where: { isActive: true } });
}, 300); // Cache for 5 minutes
```

### Cache Keys Strategy

```typescript
const CACHE_KEYS = {
  pools: {
    list: () => 'pools:list',
    detail: (id: number) => `pools:${id}`,
    members: (id: number) => `pools:${id}:members`,
    stats: (id: number) => `pools:${id}:stats`,
  },
  players: {
    profile: (wallet: string) => `players:${wallet}`,
    stats: (id: number) => `players:${id}:stats`,
    achievements: (id: number) => `players:${id}:achievements`,
  },
  leaderboard: {
    ap: (period: string) => `leaderboard:ap:${period}`,
    hashrate: (period: string) => `leaderboard:hashrate:${period}`,
  },
};
```

### Cache Invalidation

```typescript
// Invalidate on update
async function updatePool(poolId: number, data: UpdateData) {
  // Update database
  const pool = await prisma.pool.update({
    where: { id: poolId },
    data,
  });

  // Invalidate cache
  await redis.del(CACHE_KEYS.pools.detail(poolId));
  await redis.del(CACHE_KEYS.pools.list());

  return pool;
}

// Pattern-based invalidation
async function invalidatePlayerCache(playerId: number) {
  const pattern = `players:${playerId}:*`;
  const keys = await redis.keys(pattern);
  if (keys.length > 0) {
    await redis.del(...keys);
  }
}
```

## API Optimization

### Response Compression

```typescript
import compression from 'compression';

app.use(compression({
  level: 6,
  threshold: 1024, // Only compress responses > 1KB
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
}));
```

### Pagination

```typescript
// Always paginate large datasets
async function getPools(page: number = 1, limit: number = 20) {
  const skip = (page - 1) * limit;

  const [pools, total] = await Promise.all([
    prisma.pool.findMany({
      skip,
      take: limit,
      orderBy: { createdAt: 'desc' },
    }),
    prisma.pool.count(),
  ]);

  return {
    pools,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  };
}
```

### Field Selection

```typescript
// Allow clients to select fields
app.get('/api/v1/players/:wallet', async (req, res) => {
  const fields = req.query.fields?.split(',') || ['id', 'walletAddress', 'achievementPoints'];

  const select = fields.reduce((acc, field) => {
    acc[field] = true;
    return acc;
  }, {});

  const player = await prisma.player.findUnique({
    where: { walletAddress: req.params.wallet },
    select,
  });

  res.json(player);
});
```

## Frontend Optimization

### Code Splitting

```typescript
// React lazy loading
import { lazy, Suspense } from 'react';

const Pools = lazy(() => import('./pages/Pools'));
const Achievements = lazy(() => import('./pages/Achievements'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/pools" element={<Pools />} />
        <Route path="/achievements" element={<Achievements />} />
      </Routes>
    </Suspense>
  );
}
```

### Memoization

```typescript
import { useMemo, useCallback } from 'react';

function PoolList({ pools }) {
  // Memoize expensive calculations
  const sortedPools = useMemo(() => {
    return pools.sort((a, b) => b.totalHashrate - a.totalHashrate);
  }, [pools]);

  // Memoize callbacks
  const handleJoinPool = useCallback((poolId) => {
    joinPool(poolId);
  }, []);

  return (
    <div>
      {sortedPools.map(pool => (
        <PoolCard key={pool.id} pool={pool} onJoin={handleJoinPool} />
      ))}
    </div>
  );
}
```

### Virtual Scrolling

```typescript
import { FixedSizeList } from 'react-window';

function LeaderboardList({ players }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <PlayerCard player={players[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={players.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

## WebSocket Optimization

### Message Batching

```typescript
class MessageBatcher {
  private batch: any[] = [];
  private timer: NodeJS.Timeout | null = null;

  add(message: any) {
    this.batch.push(message);

    if (!this.timer) {
      this.timer = setTimeout(() => this.flush(), 100);
    }
  }

  flush() {
    if (this.batch.length > 0) {
      socket.emit('batch', this.batch);
      this.batch = [];
    }
    this.timer = null;
  }
}
```

### Room-based Broadcasting

```typescript
// Only broadcast to relevant users
io.to(`pool:${poolId}`).emit('pool_update', data);

// Don't broadcast to everyone
// io.emit('pool_update', data); // BAD
```

## CDN Configuration

### Static Asset Caching

```nginx
# Nginx configuration
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(json)$ {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

### CloudFlare Settings

```
- Enable Auto Minify (CSS, JS, HTML)
- Enable Brotli compression
- Set Browser Cache TTL: 4 hours
- Enable Rocket Loader for JS
- Use Polish for image optimization
```

## Monitoring Performance

### Application Metrics

```typescript
import prometheus from 'prom-client';

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
});

app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode.toString())
      .observe(duration);
  });

  next();
});
```

### Database Query Monitoring

```typescript
// Log slow queries
prisma.$on('query', (e) => {
  if (e.duration > 1000) {
    logger.warn('Slow query detected', {
      query: e.query,
      duration: e.duration,
      params: e.params,
    });
  }
});
```

## Load Testing

```bash
# Install k6
brew install k6  # macOS
# or
sudo apt install k6  # Ubuntu

# Create test script (load-test.js)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp up
    { duration: '3m', target: 100 }, // Stay at 100 users
    { duration: '1m', target: 0 },   // Ramp down
  ],
};

export default function() {
  const res = http.get('http://localhost:5000/api/v1/pools');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}

# Run test
k6 run load-test.js
```

## Performance Targets

- **API Response Time**: < 200ms (p95)
- **Database Queries**: < 50ms (p95)
- **Cache Hit Rate**: > 80%
- **Page Load Time**: < 2s
- **Time to Interactive**: < 3s
- **WebSocket Latency**: < 100ms
- **Throughput**: > 1000 req/s

## Continuous Optimization

1. **Regular Monitoring**: Review metrics weekly
2. **Query Analysis**: Identify slow queries monthly
3. **Load Testing**: Run tests before major releases
4. **Cache Tuning**: Adjust TTLs based on hit rates
5. **Index Review**: Add indexes for frequently queried fields
6. **Code Profiling**: Profile hot paths quarterly
7. **Dependency Updates**: Keep packages current
8. **Database Maintenance**: Vacuum and analyze weekly
