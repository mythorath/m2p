# Achievement Creation Guide

## Table of Contents
- [Overview](#overview)
- [Achievement System Architecture](#achievement-system-architecture)
- [Creating Achievements](#creating-achievements)
- [Achievement Types](#achievement-types)
- [Progress Tracking](#progress-tracking)
- [Testing Achievements](#testing-achievements)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

The M2P achievement system rewards players for completing specific tasks and reaching milestones. Achievements award Achievement Points (AP) and provide progression incentives.

### Achievement Tiers

- **Bronze** (10-50 AP) - Beginner achievements
- **Silver** (50-100 AP) - Intermediate achievements
- **Gold** (100-250 AP) - Advanced achievements
- **Platinum** (250-500 AP) - Expert achievements
- **Diamond** (500+ AP) - Legendary achievements

## Achievement System Architecture

```
AchievementService
    │
    ├── AchievementTracker (Progress tracking)
    ├── AchievementValidator (Requirement checking)
    ├── AchievementUnlocker (Unlock handling)
    └── AchievementNotifier (Event notifications)
```

### Database Schema

```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    tier VARCHAR(20) NOT NULL,
    ap_reward INTEGER NOT NULL,
    icon_url VARCHAR(255),
    requirements JSONB NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_achievements (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    achievement_id INTEGER REFERENCES achievements(id),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress JSONB,
    UNIQUE(player_id, achievement_id)
);
```

## Creating Achievements

### Step 1: Define Achievement

```typescript
// src/types/achievements.ts

export interface Achievement {
  id: number;
  name: string;
  description: string;
  tier: AchievementTier;
  apReward: number;
  iconUrl?: string;
  requirements: AchievementRequirements;
  isHidden: boolean;
  category: AchievementCategory;
}

export type AchievementTier =
  | 'Bronze'
  | 'Silver'
  | 'Gold'
  | 'Platinum'
  | 'Diamond';

export type AchievementCategory =
  | 'pools'
  | 'mining'
  | 'social'
  | 'rewards'
  | 'special';

export interface AchievementRequirements {
  type: string;
  target?: number;
  conditions?: Record<string, any>;
}
```

### Step 2: Create Achievement Data

```typescript
// Database seed or migration

const newAchievement = {
  name: 'Hash Master',
  description: 'Reach 1,000,000 total hashrate',
  tier: 'Gold',
  apReward: 100,
  iconUrl: '/icons/hash-master.png',
  category: 'mining',
  isHidden: false,
  requirements: {
    type: 'hashrate',
    target: 1000000,
  }
};

await prisma.achievement.create({
  data: newAchievement
});
```

### Step 3: Implement Requirement Checker

```typescript
// src/services/achievements/checkers/HashrateChecker.ts

export class HashrateChecker implements AchievementChecker {
  async check(
    player: Player,
    achievement: Achievement
  ): Promise<CheckResult> {
    const requirements = achievement.requirements;
    const target = requirements.target || 0;

    // Get player's current hashrate
    const currentHashrate = await this.getPlayerHashrate(player.id);

    // Calculate progress
    const progress = {
      current: currentHashrate,
      required: target,
      percentage: Math.min((currentHashrate / target) * 100, 100)
    };

    // Check if requirement is met
    const unlocked = currentHashrate >= target;

    return {
      unlocked,
      progress
    };
  }

  private async getPlayerHashrate(playerId: number): Promise<number> {
    const poolMembers = await prisma.poolMember.findMany({
      where: { playerId, isActive: true },
      select: { hashrate: true }
    });

    return poolMembers.reduce((sum, m) => sum + m.hashrate, 0);
  }
}
```

### Step 4: Register Checker

```typescript
// src/services/achievements/AchievementService.ts

export class AchievementService {
  private checkers: Map<string, AchievementChecker> = new Map();

  constructor() {
    this.registerCheckers();
  }

  private registerCheckers(): void {
    this.checkers.set('hashrate', new HashrateChecker());
    this.checkers.set('pools_joined', new PoolsJoinedChecker());
    this.checkers.set('rewards_earned', new RewardsEarnedChecker());
    this.checkers.set('shares_submitted', new SharesSubmittedChecker());
    // Add your custom checker
  }

  async checkAchievement(
    playerId: number,
    achievementId: number
  ): Promise<CheckResult> {
    const player = await this.getPlayer(playerId);
    const achievement = await this.getAchievement(achievementId);

    const checker = this.checkers.get(achievement.requirements.type);
    if (!checker) {
      throw new Error(`No checker for type: ${achievement.requirements.type}`);
    }

    return checker.check(player, achievement);
  }
}
```

## Achievement Types

### 1. Cumulative Achievements

Track cumulative progress over time.

```typescript
// Example: Total Rewards Earned

const achievement = {
  name: 'Crypto Millionaire',
  description: 'Earn 1,000,000 total rewards',
  tier: 'Platinum',
  apReward: 500,
  category: 'rewards',
  requirements: {
    type: 'rewards_earned',
    target: 1000000,
  }
};

class RewardsEarnedChecker implements AchievementChecker {
  async check(player: Player, achievement: Achievement): Promise<CheckResult> {
    const totalRewards = await prisma.transaction.aggregate({
      where: {
        playerId: player.id,
        type: 'reward',
      },
      _sum: {
        amount: true,
      }
    });

    const earned = totalRewards._sum.amount || 0;
    const target = achievement.requirements.target;

    return {
      unlocked: earned >= target,
      progress: {
        current: earned,
        required: target,
        percentage: (earned / target) * 100
      }
    };
  }
}
```

### 2. Milestone Achievements

Trigger at specific milestones.

```typescript
// Example: Join Specific Number of Pools

const achievement = {
  name: 'Pool Hopper',
  description: 'Join 10 different pools',
  tier: 'Silver',
  apReward: 75,
  category: 'pools',
  requirements: {
    type: 'pools_joined',
    target: 10,
  }
};

class PoolsJoinedChecker implements AchievementChecker {
  async check(player: Player, achievement: Achievement): Promise<CheckResult> {
    const joinedPools = await prisma.poolMember.count({
      where: { playerId: player.id },
      distinct: ['poolId']
    });

    const target = achievement.requirements.target;

    return {
      unlocked: joinedPools >= target,
      progress: {
        current: joinedPools,
        required: target,
        percentage: (joinedPools / target) * 100
      }
    };
  }
}
```

### 3. Conditional Achievements

Require specific conditions to be met.

```typescript
// Example: Join a pool with verification level 3

const achievement = {
  name: 'Elite Member',
  description: 'Join a premium pool',
  tier: 'Gold',
  apReward: 150,
  category: 'pools',
  requirements: {
    type: 'pool_joined',
    conditions: {
      poolType: 'premium',
      verificationLevel: 3,
    }
  }
};

class PoolJoinedChecker implements AchievementChecker {
  async check(player: Player, achievement: Achievement): Promise<CheckResult> {
    const conditions = achievement.requirements.conditions || {};

    // Check if player joined pool matching conditions
    const joined = await prisma.poolMember.findFirst({
      where: {
        playerId: player.id,
        pool: {
          type: conditions.poolType,
        }
      },
      include: {
        pool: true,
      }
    });

    // Check verification level
    const verified = player.verificationLevel >= conditions.verificationLevel;

    const unlocked = !!joined && verified;

    return {
      unlocked,
      progress: {
        current: unlocked ? 1 : 0,
        required: 1,
        percentage: unlocked ? 100 : 0
      }
    };
  }
}
```

### 4. Time-based Achievements

Track progress over time periods.

```typescript
// Example: Submit shares 7 days in a row

const achievement = {
  name: 'Dedicated Miner',
  description: 'Submit shares 7 days in a row',
  tier: 'Gold',
  apReward: 200,
  category: 'mining',
  requirements: {
    type: 'consecutive_days',
    target: 7,
    conditions: {
      activity: 'submit_share'
    }
  }
};

class ConsecutiveDaysChecker implements AchievementChecker {
  async check(player: Player, achievement: Achievement): Promise<CheckResult> {
    const target = achievement.requirements.target;
    const activity = achievement.requirements.conditions?.activity;

    // Get activity log
    const activities = await prisma.activityLog.findMany({
      where: {
        playerId: player.id,
        activityType: activity,
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    // Calculate consecutive days
    const consecutiveDays = this.calculateConsecutiveDays(activities);

    return {
      unlocked: consecutiveDays >= target,
      progress: {
        current: consecutiveDays,
        required: target,
        percentage: (consecutiveDays / target) * 100
      }
    };
  }

  private calculateConsecutiveDays(activities: Activity[]): number {
    if (activities.length === 0) return 0;

    let consecutive = 1;
    let lastDate = new Date(activities[0].createdAt);

    for (let i = 1; i < activities.length; i++) {
      const currentDate = new Date(activities[i].createdAt);
      const diffDays = this.daysBetween(lastDate, currentDate);

      if (diffDays === 1) {
        consecutive++;
        lastDate = currentDate;
      } else {
        break;
      }
    }

    return consecutive;
  }
}
```

### 5. Hidden Achievements

Achievements that are not visible until unlocked.

```typescript
const achievement = {
  name: 'Secret Master',
  description: 'Discovered the secret achievement!',
  tier: 'Diamond',
  apReward: 1000,
  category: 'special',
  isHidden: true,  // Not shown until unlocked
  requirements: {
    type: 'secret_action',
    conditions: {
      action: 'konami_code'
    }
  }
};
```

## Progress Tracking

### Automatic Tracking

Track progress automatically on game events:

```typescript
// src/services/achievements/AchievementTracker.ts

export class AchievementTracker {
  async onEvent(event: GameEvent): Promise<void> {
    const { type, playerId, data } = event;

    // Update progress for all relevant achievements
    const achievements = await this.getRelevantAchievements(type);

    for (const achievement of achievements) {
      await this.updateProgress(playerId, achievement, data);

      // Check if achievement is now unlocked
      const result = await this.achievementService.checkAchievement(
        playerId,
        achievement.id
      );

      if (result.unlocked) {
        await this.unlockAchievement(playerId, achievement.id);
      }
    }
  }

  private async updateProgress(
    playerId: number,
    achievement: Achievement,
    eventData: any
  ): Promise<void> {
    // Get current progress
    const current = await prisma.playerAchievement.findUnique({
      where: {
        playerId_achievementId: {
          playerId,
          achievementId: achievement.id
        }
      }
    });

    // Calculate new progress
    const newProgress = this.calculateProgress(
      achievement,
      current?.progress,
      eventData
    );

    // Save progress
    await prisma.playerAchievement.upsert({
      where: {
        playerId_achievementId: {
          playerId,
          achievementId: achievement.id
        }
      },
      update: { progress: newProgress },
      create: {
        playerId,
        achievementId: achievement.id,
        progress: newProgress
      }
    });
  }
}
```

### Event Mapping

```typescript
// Map game events to achievement types
const EVENT_ACHIEVEMENT_MAP = {
  'share_submitted': ['shares_submitted', 'consecutive_days'],
  'pool_joined': ['pools_joined', 'pool_joined'],
  'reward_earned': ['rewards_earned'],
  'verification_completed': ['verification_level'],
  // Add more mappings
};
```

## Testing Achievements

### Unit Tests

```typescript
// tests/unit/achievements/HashrateChecker.test.ts

describe('HashrateChecker', () => {
  let checker: HashrateChecker;

  beforeEach(() => {
    checker = new HashrateChecker();
  });

  it('should unlock when hashrate reaches target', async () => {
    const player = { id: 1, hashrate: 1500000 };
    const achievement = {
      requirements: { type: 'hashrate', target: 1000000 }
    };

    const result = await checker.check(player, achievement);

    expect(result.unlocked).toBe(true);
    expect(result.progress.percentage).toBe(100);
  });

  it('should track progress correctly', async () => {
    const player = { id: 1, hashrate: 500000 };
    const achievement = {
      requirements: { type: 'hashrate', target: 1000000 }
    };

    const result = await checker.check(player, achievement);

    expect(result.unlocked).toBe(false);
    expect(result.progress.percentage).toBe(50);
  });
});
```

### Integration Tests

```typescript
// tests/integration/achievementUnlock.test.ts

describe('Achievement Unlock', () => {
  it('should unlock achievement when requirements met', async () => {
    const player = await createTestPlayer();

    // Perform action that should unlock achievement
    await joinPools(player.id, 10);

    // Check achievement status
    const achievement = await prisma.achievement.findFirst({
      where: { name: 'Pool Hopper' }
    });

    const unlocked = await prisma.playerAchievement.findUnique({
      where: {
        playerId_achievementId: {
          playerId: player.id,
          achievementId: achievement.id
        }
      }
    });

    expect(unlocked).toBeDefined();
    expect(unlocked.unlockedAt).toBeDefined();

    // Check AP was awarded
    const updatedPlayer = await prisma.player.findUnique({
      where: { id: player.id }
    });

    expect(updatedPlayer.achievementPoints).toBe(achievement.apReward);
  });
});
```

## Examples

### Example 1: First Pool Achievement

```typescript
const firstPoolAchievement = {
  name: 'First Steps',
  description: 'Join your first mining pool',
  tier: 'Bronze',
  apReward: 10,
  iconUrl: '/icons/first-steps.png',
  category: 'pools',
  isHidden: false,
  requirements: {
    type: 'pools_joined',
    target: 1,
  }
};
```

### Example 2: Power Miner Achievement

```typescript
const powerMinerAchievement = {
  name: 'Power Miner',
  description: 'Submit 10,000 shares',
  tier: 'Gold',
  apReward: 150,
  iconUrl: '/icons/power-miner.png',
  category: 'mining',
  isHidden: false,
  requirements: {
    type: 'shares_submitted',
    target: 10000,
  }
};
```

### Example 3: VIP Achievement

```typescript
const vipAchievement = {
  name: 'VIP Status',
  description: 'Reach verification level 3',
  tier: 'Platinum',
  apReward: 300,
  iconUrl: '/icons/vip.png',
  category: 'special',
  isHidden: false,
  requirements: {
    type: 'verification_level',
    target: 3,
  }
};
```

### Example 4: Social Achievement

```typescript
const socialAchievement = {
  name: 'Team Player',
  description: 'Be a member of 5 active pools simultaneously',
  tier: 'Silver',
  apReward: 100,
  iconUrl: '/icons/team-player.png',
  category: 'social',
  isHidden: false,
  requirements: {
    type: 'concurrent_pools',
    target: 5,
  }
};
```

### Example 5: Special Event Achievement

```typescript
const eventAchievement = {
  name: 'Beta Tester',
  description: 'Participated in the beta test',
  tier: 'Diamond',
  apReward: 500,
  iconUrl: '/icons/beta-tester.png',
  category: 'special',
  isHidden: false,
  requirements: {
    type: 'special_event',
    conditions: {
      eventId: 'beta_2025',
      dateRange: {
        start: '2025-01-01',
        end: '2025-03-31'
      }
    }
  }
};
```

## Achievement Chains

Create series of related achievements:

```typescript
const achievementChain = [
  {
    name: 'Novice Miner',
    tier: 'Bronze',
    apReward: 10,
    requirements: { type: 'shares_submitted', target: 100 }
  },
  {
    name: 'Apprentice Miner',
    tier: 'Silver',
    apReward: 50,
    requirements: {
      type: 'shares_submitted',
      target: 1000,
      prerequisite: 'Novice Miner'
    }
  },
  {
    name: 'Expert Miner',
    tier: 'Gold',
    apReward: 150,
    requirements: {
      type: 'shares_submitted',
      target: 10000,
      prerequisite: 'Apprentice Miner'
    }
  },
  {
    name: 'Master Miner',
    tier: 'Platinum',
    apReward: 400,
    requirements: {
      type: 'shares_submitted',
      target: 100000,
      prerequisite: 'Expert Miner'
    }
  }
];
```

## Best Practices

1. **Clear Descriptions** - Make requirements obvious
2. **Balanced Rewards** - AP rewards should match difficulty
3. **Varied Categories** - Cover different aspects of gameplay
4. **Progressive Difficulty** - Create achievement chains
5. **Hidden Achievements** - Add surprise discoveries
6. **Unique Icons** - Visual distinction for each tier
7. **Track Progress** - Always show progress when possible
8. **Test Thoroughly** - Verify unlock conditions work correctly
9. **Avoid Grinding** - Don't make achievements too repetitive
10. **Celebrate Unlocks** - Show notifications and effects

## API Integration

### Create Achievement Endpoint

```typescript
// POST /api/v1/admin/achievements
router.post('/achievements', adminAuth, async (req, res) => {
  const achievement = await achievementService.createAchievement(req.body);
  res.status(201).json(achievement);
});
```

### Manual Unlock (Admin)

```typescript
// POST /api/v1/admin/achievements/:id/unlock
router.post('/achievements/:id/unlock', adminAuth, async (req, res) => {
  const { playerId } = req.body;
  await achievementService.unlockAchievement(playerId, req.params.id);
  res.json({ success: true });
});
```

## Frontend Integration

### Display Achievement Card

```typescript
// components/achievements/AchievementCard.tsx
export const AchievementCard: React.FC<{ achievement: Achievement }> = ({
  achievement
}) => {
  const progress = useAchievementProgress(achievement.id);

  return (
    <div className={`achievement-card ${achievement.tier.toLowerCase()}`}>
      <img src={achievement.iconUrl} alt={achievement.name} />
      <h3>{achievement.name}</h3>
      <p>{achievement.description}</p>
      <div className="ap-reward">{achievement.apReward} AP</div>

      {!progress.unlocked && (
        <ProgressBar
          current={progress.current}
          target={progress.required}
          percentage={progress.percentage}
        />
      )}

      {progress.unlocked && (
        <div className="unlocked-badge">
          ✓ Unlocked {new Date(progress.unlockedAt).toLocaleDateString()}
        </div>
      )}
    </div>
  );
};
```

## Troubleshooting

### Achievement Not Unlocking

1. Check requirement checker logic
2. Verify event tracking is working
3. Check database progress values
4. Ensure achievement is active
5. Review logs for errors

### Progress Not Updating

1. Verify events are being emitted
2. Check event mapping configuration
3. Ensure tracker is listening to events
4. Review database transactions

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
