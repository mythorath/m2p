# Pool Integration Guide

## Table of Contents
- [Overview](#overview)
- [Pool Types](#pool-types)
- [Creating a New Pool Type](#creating-a-new-pool-type)
- [Pool Configuration](#pool-configuration)
- [Reward Distribution](#reward-distribution)
- [Custom Pool Logic](#custom-pool-logic)
- [Testing Pool Implementation](#testing-pool-implementation)
- [Examples](#examples)

## Overview

M2P supports multiple pool types with different mechanics, reward structures, and gameplay features. This guide explains how to integrate new pool types into the system.

### Pool Architecture

```
PoolService (Base)
    │
    ├── StandardPool
    ├── PremiumPool
    ├── TournamentPool
    └── CustomPool (Your Implementation)
```

## Pool Types

### Built-in Pool Types

#### 1. Standard Pool
- Basic pool mechanics
- Fixed difficulty
- Proportional reward distribution
- No special features

#### 2. Premium Pool
- Higher rewards
- Lower fees
- Requires verification level 2+
- Limited slots

#### 3. Tournament Pool
- Time-limited
- Leaderboard-based rewards
- Entry requirements
- Special achievements

### Pool Properties

All pools share these core properties:

```typescript
interface Pool {
  id: number;
  name: string;
  type: string;                // Pool type identifier
  difficulty: number;          // Mining difficulty
  maxPlayers: number;          // Maximum members
  currentPlayers: number;      // Current member count
  totalHashrate: bigint;       // Combined hashrate
  rewardPerBlock: Decimal;     // Reward amount
  feePercentage: Decimal;      // Pool fee (0-100)
  ownerWallet?: string;        // Pool owner
  isActive: boolean;           // Active status
  config: PoolConfig;          // Type-specific config
  stats: PoolStats;            // Pool statistics
  createdAt: Date;
}
```

## Creating a New Pool Type

### Step 1: Define Pool Configuration

Create configuration schema in `src/types/pools.ts`:

```typescript
// Define your pool's configuration
export interface CustomPoolConfig {
  // Custom configuration fields
  bonusMultiplier: number;
  specialFeature: boolean;
  minimumHashrate: number;
  // ... other fields
}

// Add to PoolConfig union type
export type PoolConfig =
  | StandardPoolConfig
  | PremiumPoolConfig
  | TournamentPoolConfig
  | CustomPoolConfig;  // Your new type
```

### Step 2: Create Pool Class

Create `src/services/pools/CustomPool.ts`:

```typescript
import { BasePool } from './BasePool';
import { CustomPoolConfig } from '../../types/pools';

export class CustomPool extends BasePool {
  private config: CustomPoolConfig;

  constructor(poolData: Pool) {
    super(poolData);
    this.config = poolData.config as CustomPoolConfig;
    this.validateConfig();
  }

  /**
   * Validate pool configuration
   */
  private validateConfig(): void {
    if (this.config.bonusMultiplier < 1 || this.config.bonusMultiplier > 10) {
      throw new Error('Invalid bonus multiplier');
    }

    if (this.config.minimumHashrate < 0) {
      throw new Error('Invalid minimum hashrate');
    }
  }

  /**
   * Check if player can join this pool
   */
  async canJoin(playerId: number): Promise<boolean> {
    // Check base requirements
    const baseCheck = await super.canJoin(playerId);
    if (!baseCheck) return false;

    // Check custom requirements
    const player = await this.getPlayer(playerId);

    // Example: Require minimum hashrate
    if (player.hashrate < this.config.minimumHashrate) {
      return false;
    }

    return true;
  }

  /**
   * Calculate reward for player
   */
  calculateReward(
    playerId: number,
    shares: number,
    totalShares: number
  ): Decimal {
    // Base reward calculation
    let reward = super.calculateReward(playerId, shares, totalShares);

    // Apply bonus multiplier
    if (this.config.specialFeature) {
      reward = reward.times(this.config.bonusMultiplier);
    }

    return reward;
  }

  /**
   * Handle share submission
   */
  async submitShare(
    playerId: number,
    share: Share
  ): Promise<ShareResult> {
    // Validate share
    if (!this.validateShare(share)) {
      return { accepted: false, reason: 'Invalid share' };
    }

    // Custom share processing logic
    const result = await super.submitShare(playerId, share);

    // Additional processing for this pool type
    if (result.accepted && this.config.specialFeature) {
      await this.processSpecialFeature(playerId, share);
    }

    return result;
  }

  /**
   * Custom feature implementation
   */
  private async processSpecialFeature(
    playerId: number,
    share: Share
  ): Promise<void> {
    // Implement your custom logic
    // Example: Award bonus AP
    await this.awardBonusAP(playerId, 10);
  }

  /**
   * Get pool statistics
   */
  async getStats(): Promise<PoolStats> {
    const baseStats = await super.getStats();

    // Add custom statistics
    return {
      ...baseStats,
      customStat1: await this.calculateCustomStat1(),
      customStat2: await this.calculateCustomStat2(),
    };
  }

  /**
   * Handle pool events
   */
  protected async onMemberJoined(playerId: number): Promise<void> {
    await super.onMemberJoined(playerId);

    // Custom logic when member joins
    // Example: Announce in pool chat
    await this.broadcastMessage({
      type: 'member_joined',
      playerId,
      message: 'Welcome to the custom pool!'
    });
  }

  protected async onMemberLeft(playerId: number): Promise<void> {
    await super.onMemberLeft(playerId);

    // Custom logic when member leaves
  }
}
```

### Step 3: Register Pool Type

Update `src/services/PoolFactory.ts`:

```typescript
import { CustomPool } from './pools/CustomPool';

export class PoolFactory {
  static createPool(poolData: Pool): BasePool {
    switch (poolData.type) {
      case 'standard':
        return new StandardPool(poolData);
      case 'premium':
        return new PremiumPool(poolData);
      case 'tournament':
        return new TournamentPool(poolData);
      case 'custom':  // Your new type
        return new CustomPool(poolData);
      default:
        throw new Error(`Unknown pool type: ${poolData.type}`);
    }
  }
}
```

### Step 4: Add Database Migration

Create migration for pool configuration:

```bash
npm run db:migrate:create -- --name add_custom_pool_type
```

Update migration file:

```sql
-- Update pool type enum
ALTER TYPE pool_type ADD VALUE 'custom';

-- Add any new columns needed
ALTER TABLE pools ADD COLUMN IF NOT EXISTS custom_data JSONB;
```

### Step 5: Create API Endpoints

Add endpoints in `src/routes/pools.ts`:

```typescript
/**
 * Create custom pool
 * POST /api/v1/pools/custom
 */
router.post('/custom', authMiddleware, async (req, res) => {
  const { name, config } = req.body;

  // Validate configuration
  const validatedConfig = customPoolConfigSchema.parse(config);

  // Create pool
  const pool = await poolService.createPool({
    name,
    type: 'custom',
    config: validatedConfig,
    ownerWallet: req.user.wallet
  });

  res.status(201).json(pool);
});

/**
 * Get custom pool stats
 * GET /api/v1/pools/:id/custom-stats
 */
router.get('/:id/custom-stats', async (req, res) => {
  const pool = await poolService.getPool(req.params.id);

  if (pool.type !== 'custom') {
    return res.status(400).json({
      error: 'Not a custom pool'
    });
  }

  const customPool = PoolFactory.createPool(pool) as CustomPool;
  const stats = await customPool.getCustomStats();

  res.json(stats);
});
```

### Step 6: Add Frontend Support

Create React component for custom pool:

```typescript
// components/pools/CustomPoolCard.tsx
import React from 'react';
import { Pool } from '../../types';

interface Props {
  pool: Pool;
}

export const CustomPoolCard: React.FC<Props> = ({ pool }) => {
  const config = pool.config as CustomPoolConfig;

  return (
    <div className="pool-card custom-pool">
      <h3>{pool.name}</h3>

      <div className="pool-stats">
        <div>Difficulty: {pool.difficulty}</div>
        <div>Bonus Multiplier: {config.bonusMultiplier}x</div>
        <div>Min Hashrate: {config.minimumHashrate}</div>
      </div>

      {config.specialFeature && (
        <div className="special-badge">
          Special Feature Enabled!
        </div>
      )}

      <button onClick={() => joinPool(pool.id)}>
        Join Pool
      </button>
    </div>
  );
};
```

## Pool Configuration

### Configuration Schema

Use Zod for validation:

```typescript
import { z } from 'zod';

export const customPoolConfigSchema = z.object({
  bonusMultiplier: z.number().min(1).max(10),
  specialFeature: z.boolean(),
  minimumHashrate: z.number().min(0),
  maxDailyReward: z.string().optional(),
  allowedVerificationLevels: z.array(z.number()).optional(),
});

export type CustomPoolConfig = z.infer<typeof customPoolConfigSchema>;
```

### Default Configuration

```typescript
export const DEFAULT_CUSTOM_POOL_CONFIG: CustomPoolConfig = {
  bonusMultiplier: 1.5,
  specialFeature: true,
  minimumHashrate: 100000,
  maxDailyReward: '1000.0',
  allowedVerificationLevels: [1, 2, 3],
};
```

## Reward Distribution

### Custom Reward Algorithm

```typescript
class CustomPool extends BasePool {
  /**
   * Distribute rewards with custom logic
   */
  async distributeRewards(blockReward: Decimal): Promise<void> {
    const members = await this.getActiveMembers();
    const totalShares = await this.getTotalShares();

    for (const member of members) {
      // Calculate base reward
      const baseReward = blockReward
        .times(member.shares)
        .dividedBy(totalShares);

      // Apply custom modifiers
      let finalReward = baseReward;

      // Bonus for high performers
      if (member.hashrate > this.config.minimumHashrate * 2) {
        finalReward = finalReward.times(1.2);
      }

      // Apply pool fee
      const fee = finalReward.times(this.pool.feePercentage).dividedBy(100);
      finalReward = finalReward.minus(fee);

      // Cap at max daily reward if configured
      if (this.config.maxDailyReward) {
        const maxReward = new Decimal(this.config.maxDailyReward);
        finalReward = Decimal.min(finalReward, maxReward);
      }

      // Award reward
      await this.awardReward(member.playerId, finalReward);

      // Emit event
      this.emit('reward_distributed', {
        playerId: member.playerId,
        amount: finalReward.toString(),
        shares: member.shares,
      });
    }
  }
}
```

## Custom Pool Logic

### Advanced Features

#### Dynamic Difficulty Adjustment

```typescript
class CustomPool extends BasePool {
  /**
   * Adjust difficulty based on pool hashrate
   */
  async adjustDifficulty(): Promise<void> {
    const avgHashrate = await this.getAverageHashrate();
    const targetBlockTime = 600; // seconds

    // Calculate new difficulty
    const currentBlockTime = await this.getAverageBlockTime();
    const ratio = currentBlockTime / targetBlockTime;

    const newDifficulty = Math.floor(this.pool.difficulty * ratio);

    // Apply bounds
    const minDifficulty = 100;
    const maxDifficulty = 1000000;
    const boundedDifficulty = Math.min(
      Math.max(newDifficulty, minDifficulty),
      maxDifficulty
    );

    // Update difficulty
    await this.updateDifficulty(boundedDifficulty);

    this.emit('difficulty_adjusted', {
      oldDifficulty: this.pool.difficulty,
      newDifficulty: boundedDifficulty,
    });
  }
}
```

#### Time-based Events

```typescript
class CustomPool extends BasePool {
  private eventScheduler: NodeSchedule;

  constructor(poolData: Pool) {
    super(poolData);
    this.setupEvents();
  }

  private setupEvents(): void {
    // Happy hour: Double rewards every day 6-8 PM
    this.eventScheduler.schedule('0 18 * * *', async () => {
      await this.startHappyHour();
    });

    this.eventScheduler.schedule('0 20 * * *', async () => {
      await this.endHappyHour();
    });
  }

  private async startHappyHour(): Promise<void> {
    this.config.bonusMultiplier *= 2;
    this.broadcastMessage({
      type: 'event_started',
      message: 'Happy Hour: 2x rewards!',
    });
  }
}
```

#### Leaderboard Integration

```typescript
class CustomPool extends BasePool {
  /**
   * Get pool leaderboard
   */
  async getLeaderboard(period: 'daily' | 'weekly' | 'all-time'): Promise<Leaderboard> {
    const timeRange = this.getTimeRange(period);

    const members = await prisma.poolMember.findMany({
      where: {
        poolId: this.pool.id,
        isActive: true,
        joinedAt: { gte: timeRange.start },
      },
      include: {
        player: true,
      },
      orderBy: {
        sharesSubmitted: 'desc',
      },
      take: 100,
    });

    return members.map((member, index) => ({
      rank: index + 1,
      playerId: member.playerId,
      username: member.player.username,
      shares: member.sharesSubmitted,
      hashrate: member.hashrate,
      rewards: member.rewardsEarned,
    }));
  }
}
```

## Testing Pool Implementation

### Unit Tests

```typescript
// tests/unit/CustomPool.test.ts
import { CustomPool } from '../../src/services/pools/CustomPool';

describe('CustomPool', () => {
  let customPool: CustomPool;

  beforeEach(() => {
    const poolData = {
      id: 1,
      name: 'Test Custom Pool',
      type: 'custom',
      config: {
        bonusMultiplier: 2,
        specialFeature: true,
        minimumHashrate: 100000,
      },
    };
    customPool = new CustomPool(poolData);
  });

  describe('canJoin', () => {
    it('should allow player with sufficient hashrate', async () => {
      const player = { id: 1, hashrate: 200000 };
      const result = await customPool.canJoin(player.id);
      expect(result).toBe(true);
    });

    it('should reject player with insufficient hashrate', async () => {
      const player = { id: 2, hashrate: 50000 };
      const result = await customPool.canJoin(player.id);
      expect(result).toBe(false);
    });
  });

  describe('calculateReward', () => {
    it('should apply bonus multiplier', () => {
      const reward = customPool.calculateReward(1, 100, 1000);
      const expectedReward = (100 / 1000) * 50 * 2; // base * multiplier
      expect(reward.toNumber()).toBeCloseTo(expectedReward);
    });
  });
});
```

### Integration Tests

```typescript
// tests/integration/customPool.test.ts
import request from 'supertest';
import { app } from '../../src/app';

describe('Custom Pool API', () => {
  describe('POST /api/v1/pools/custom', () => {
    it('should create custom pool', async () => {
      const response = await request(app)
        .post('/api/v1/pools/custom')
        .set('Authorization', `Bearer ${token}`)
        .send({
          name: 'My Custom Pool',
          config: {
            bonusMultiplier: 1.5,
            specialFeature: true,
            minimumHashrate: 100000,
          },
        });

      expect(response.status).toBe(201);
      expect(response.body.type).toBe('custom');
    });
  });
});
```

## Examples

### Example 1: VIP Pool

```typescript
export class VIPPool extends BasePool {
  async canJoin(playerId: number): Promise<boolean> {
    const player = await this.getPlayer(playerId);

    // Require verification level 3
    if (player.verificationLevel < 3) {
      return false;
    }

    // Require minimum 10,000 AP
    if (player.achievementPoints < 10000) {
      return false;
    }

    return super.canJoin(playerId);
  }

  calculateReward(playerId: number, shares: number, totalShares: number): Decimal {
    const baseReward = super.calculateReward(playerId, shares, totalShares);
    // VIP pools have 0% fee
    return baseReward;
  }
}
```

### Example 2: Team Pool

```typescript
export class TeamPool extends BasePool {
  private teams: Map<number, number[]> = new Map(); // teamId => playerIds

  async joinAsTeam(playerIds: number[], teamName: string): Promise<void> {
    // Validate all players can join
    for (const playerId of playerIds) {
      if (!await this.canJoin(playerId)) {
        throw new Error(`Player ${playerId} cannot join`);
      }
    }

    // Create team
    const teamId = await this.createTeam(teamName);
    this.teams.set(teamId, playerIds);

    // Add all players
    for (const playerId of playerIds) {
      await this.addMember(playerId);
    }
  }

  async distributeRewards(blockReward: Decimal): Promise<void> {
    // Distribute to teams instead of individual players
    for (const [teamId, playerIds] of this.teams) {
      const teamShares = await this.getTeamShares(teamId);
      const teamReward = blockReward.times(teamShares).dividedBy(totalShares);

      // Split reward among team members
      const rewardPerPlayer = teamReward.dividedBy(playerIds.length);

      for (const playerId of playerIds) {
        await this.awardReward(playerId, rewardPerPlayer);
      }
    }
  }
}
```

### Example 3: Lottery Pool

```typescript
export class LotteryPool extends BasePool {
  async distributeRewards(blockReward: Decimal): Promise<void> {
    const members = await this.getActiveMembers();

    // 50% distributed proportionally
    const proportionalReward = blockReward.times(0.5);
    await super.distributeRewards(proportionalReward);

    // 50% to lottery winner
    const lotteryReward = blockReward.times(0.5);
    const winner = this.selectLotteryWinner(members);

    await this.awardReward(winner.playerId, lotteryReward);

    this.emit('lottery_winner', {
      playerId: winner.playerId,
      amount: lotteryReward.toString(),
    });
  }

  private selectLotteryWinner(members: PoolMember[]): PoolMember {
    // Weight by shares submitted
    const totalWeight = members.reduce((sum, m) => sum + m.shares, 0);
    const random = Math.random() * totalWeight;

    let cumulative = 0;
    for (const member of members) {
      cumulative += member.shares;
      if (random <= cumulative) {
        return member;
      }
    }

    return members[members.length - 1];
  }
}
```

## Best Practices

1. **Always extend BasePool** - Reuse common functionality
2. **Validate configuration** - Check all config values in constructor
3. **Document custom features** - Add JSDoc comments explaining unique behavior
4. **Write comprehensive tests** - Test all custom logic thoroughly
5. **Handle errors gracefully** - Provide clear error messages
6. **Emit events** - Use events for real-time updates
7. **Log important actions** - Help with debugging and monitoring
8. **Consider performance** - Cache expensive calculations
9. **Version your changes** - Track pool type versions for migrations
10. **Update documentation** - Keep API docs and guides current

## Troubleshooting

### Common Issues

**Issue**: Pool not appearing in list
- Check pool is marked as active
- Verify pool type is registered in PoolFactory
- Check database migration ran successfully

**Issue**: Rewards not distributing correctly
- Verify calculateReward logic
- Check for rounding errors with Decimal
- Ensure total shares calculation is correct

**Issue**: Players can't join pool
- Check canJoin logic
- Verify player meets requirements
- Check pool capacity limits

## Next Steps

1. Implement your custom pool type
2. Write comprehensive tests
3. Update API documentation
4. Create frontend components
5. Deploy and monitor

For questions or support, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
