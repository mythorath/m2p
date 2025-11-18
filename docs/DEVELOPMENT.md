# Development Setup Guide

## Table of Contents
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Database Development](#database-development)
- [Testing](#testing)
- [Code Style](#code-style)
- [Git Workflow](#git-workflow)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)

## Getting Started

### Prerequisites

- **Node.js** >= 18.0.0
- **npm** >= 9.0.0
- **PostgreSQL** >= 13
- **Redis** >= 6.0
- **Git**
- **VS Code** (recommended) or your preferred IDE

### Quick Setup

```bash
# Clone repository
git clone https://github.com/yourusername/m2p.git
cd m2p

# Install dependencies for server
cd server
npm install

# Install dependencies for client
cd ../client
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your local configuration

# Setup database
cd ../server
npm run db:setup

# Start development servers
npm run dev  # In server directory
```

In a new terminal:
```bash
cd client
npm run dev
```

### Environment Variables for Development

Create `.env` in server directory:

```env
# Application
NODE_ENV=development
PORT=5000
CLIENT_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/m2p_dev

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=dev_secret_change_in_production
JWT_EXPIRY=86400

# Logging
LOG_LEVEL=debug

# Development
ENABLE_API_DOCS=true
ENABLE_CORS=true
```

## Development Environment

### VS Code Setup

#### Recommended Extensions

Install these extensions:

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "prisma.prisma",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "dsznajder.es7-react-js-snippets",
    "christian-kohler.path-intellisense",
    "eamodio.gitlens"
  ]
}
```

#### VS Code Settings

`.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.updateImportsOnFileMove.enabled": "always"
}
```

#### Debug Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Server",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "cwd": "${workspaceFolder}/server",
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Debug Client",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/client/src"
    }
  ]
}
```

### Docker Development Environment

Use Docker for consistent development environment:

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Stop services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f app
```

## Project Structure

### Server Structure

```
server/
├── src/
│   ├── config/           # Configuration files
│   │   ├── database.ts   # Database configuration
│   │   ├── redis.ts      # Redis configuration
│   │   └── app.ts        # App configuration
│   ├── controllers/      # Request handlers
│   │   ├── authController.ts
│   │   ├── poolController.ts
│   │   └── ...
│   ├── services/         # Business logic
│   │   ├── poolService.ts
│   │   ├── achievementService.ts
│   │   └── ...
│   ├── models/           # Data models (Prisma)
│   ├── middleware/       # Express middleware
│   │   ├── auth.ts
│   │   ├── validation.ts
│   │   ├── errorHandler.ts
│   │   └── ...
│   ├── routes/           # API routes
│   │   ├── index.ts      # Route aggregator
│   │   ├── auth.ts
│   │   └── ...
│   ├── websocket/        # WebSocket handlers
│   │   ├── index.ts
│   │   └── handlers/
│   ├── utils/            # Utility functions
│   │   ├── validation.ts
│   │   ├── crypto.ts
│   │   └── ...
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   └── index.ts          # Application entry point
├── prisma/
│   ├── schema.prisma     # Database schema
│   ├── migrations/       # Migration files
│   └── seed.ts           # Seed data
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── package.json
└── tsconfig.json
```

### Client Structure

```
client/
├── src/
│   ├── components/       # React components
│   │   ├── common/       # Reusable components
│   │   ├── pools/        # Pool components
│   │   ├── achievements/ # Achievement components
│   │   └── layout/       # Layout components
│   ├── pages/            # Page components
│   │   ├── Home.tsx
│   │   ├── Pools.tsx
│   │   └── ...
│   ├── hooks/            # Custom React hooks
│   │   ├── useWallet.ts
│   │   ├── useWebSocket.ts
│   │   └── ...
│   ├── services/         # API services
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   └── wallet.ts
│   ├── store/            # State management (Redux)
│   │   ├── slices/
│   │   └── index.ts
│   ├── types/            # TypeScript types
│   ├── utils/            # Utility functions
│   ├── styles/           # Global styles
│   ├── App.tsx           # Root component
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── tests/
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## Database Development

### Using Prisma

#### Create Migration

```bash
# Make changes to prisma/schema.prisma
# Then create migration
npm run db:migrate:create -- --name add_new_field

# Apply migration
npm run db:migrate
```

#### Reset Database

```bash
# Reset and reseed database
npm run db:reset
```

#### Prisma Studio

```bash
# Open Prisma Studio (database GUI)
npx prisma studio
```

### Example Schema Addition

```prisma
// prisma/schema.prisma

model Guild {
  id          Int       @id @default(autoincrement())
  name        String    @db.VarChar(100)
  description String?   @db.Text
  ownerId     Int
  owner       Player    @relation("GuildOwner", fields: [ownerId], references: [id])
  members     Player[]  @relation("GuildMembers")
  createdAt   DateTime  @default(now())

  @@index([ownerId])
}
```

### Seed Data

Edit `prisma/seed.ts`:

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create test pools
  const pool1 = await prisma.pool.create({
    data: {
      name: 'Test Pool 1',
      type: 'standard',
      difficulty: 1000,
      maxPlayers: 100,
      rewardPerBlock: '50.0',
      feePercentage: '2.5'
    }
  });

  // Create test achievements
  const achievement1 = await prisma.achievement.create({
    data: {
      name: 'First Steps',
      description: 'Join your first pool',
      tier: 'Bronze',
      apReward: 10,
      requirements: JSON.stringify({ poolsJoined: 1 })
    }
  });
}

main()
  .catch(e => console.error(e))
  .finally(() => prisma.$disconnect());
```

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- poolService.test.ts
```

### Writing Unit Tests

Example test (`tests/unit/poolService.test.ts`):

```typescript
import { PoolService } from '../../src/services/poolService';
import { PrismaClient } from '@prisma/client';

describe('PoolService', () => {
  let poolService: PoolService;
  let prisma: PrismaClient;

  beforeAll(() => {
    prisma = new PrismaClient();
    poolService = new PoolService(prisma);
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  describe('createPool', () => {
    it('should create a new pool', async () => {
      const poolData = {
        name: 'Test Pool',
        type: 'standard',
        difficulty: 1000,
        maxPlayers: 100,
        rewardPerBlock: '50.0',
        feePercentage: '2.5'
      };

      const pool = await poolService.createPool(poolData);

      expect(pool).toBeDefined();
      expect(pool.name).toBe('Test Pool');
      expect(pool.type).toBe('standard');
    });

    it('should throw error for invalid data', async () => {
      const invalidData = {
        name: '',
        type: 'invalid'
      };

      await expect(poolService.createPool(invalidData as any))
        .rejects.toThrow();
    });
  });
});
```

### Writing Integration Tests

Example integration test (`tests/integration/poolApi.test.ts`):

```typescript
import request from 'supertest';
import { app } from '../../src/app';

describe('Pool API', () => {
  let authToken: string;

  beforeAll(async () => {
    // Get authentication token
    const response = await request(app)
      .post('/api/v1/auth/verify')
      .send({
        wallet_address: '0x123...',
        signature: '0x...',
        nonce: '123'
      });

    authToken = response.body.token;
  });

  describe('GET /api/v1/pools', () => {
    it('should return list of pools', async () => {
      const response = await request(app)
        .get('/api/v1/pools')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('pools');
      expect(Array.isArray(response.body.pools)).toBe(true);
    });
  });

  describe('POST /api/v1/pools/:id/join', () => {
    it('should join a pool', async () => {
      const response = await request(app)
        .post('/api/v1/pools/1/join')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });
  });
});
```

### E2E Tests with Playwright

```typescript
import { test, expect } from '@playwright/test';

test('user can join a pool', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:3000');

  // Connect wallet
  await page.click('button:has-text("Connect Wallet")');
  await page.click('button:has-text("MetaMask")');

  // Navigate to pools
  await page.click('a:has-text("Pools")');

  // Join first pool
  await page.click('button:has-text("Join Pool")').first();

  // Verify success
  await expect(page.locator('.toast-success')).toContainText('Successfully joined');
});
```

## Code Style

### ESLint Configuration

`.eslintrc.js`:

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    'no-console': ['warn', { allow: ['warn', 'error'] }]
  }
};
```

### Prettier Configuration

`.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "avoid"
}
```

### Naming Conventions

- **Files**: camelCase for TypeScript files, PascalCase for React components
- **Variables**: camelCase
- **Constants**: UPPER_SNAKE_CASE
- **Classes**: PascalCase
- **Interfaces**: PascalCase (prefix with I optional)
- **Types**: PascalCase

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(pools): add pool creation API

- Add POST /api/v1/pools endpoint
- Add validation for pool creation
- Add tests for pool creation

Closes #123
```

### Pre-commit Hooks

Install husky:

```bash
npm install -D husky lint-staged

# Setup
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
```

`package.json`:

```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ]
  }
}
```

## Debugging

### Backend Debugging

#### Using VS Code

1. Set breakpoints in code
2. Press F5 or use Debug panel
3. Code will pause at breakpoints

#### Using Chrome DevTools

```bash
# Start with inspector
node --inspect dist/index.js

# Open chrome://inspect in Chrome
# Click "inspect" on your app
```

#### Logging

```typescript
import { logger } from './utils/logger';

logger.debug('Debug message', { data });
logger.info('Info message');
logger.warn('Warning message');
logger.error('Error message', { error });
```

### Frontend Debugging

#### React DevTools

Install React DevTools browser extension.

#### Redux DevTools

```typescript
// In store configuration
import { configureStore } from '@reduxjs/toolkit';
import { composeWithDevTools } from 'redux-devtools-extension';

const store = configureStore({
  reducer: rootReducer,
  devTools: process.env.NODE_ENV !== 'production'
});
```

## Common Tasks

### Add New API Endpoint

1. Define route in `routes/`:
```typescript
// routes/myRoutes.ts
router.get('/my-endpoint', authMiddleware, myController.handler);
```

2. Create controller:
```typescript
// controllers/myController.ts
export const handler = async (req: Request, res: Response) => {
  // Handle request
};
```

3. Add tests
4. Update API documentation

### Add New Database Model

1. Edit `prisma/schema.prisma`
2. Create migration: `npm run db:migrate:create`
3. Apply migration: `npm run db:migrate`
4. Update TypeScript types

### Add New React Component

1. Create component file:
```typescript
// components/MyComponent.tsx
export const MyComponent: React.FC<Props> = ({ ...props }) => {
  return <div>...</div>;
};
```

2. Add tests:
```typescript
// components/MyComponent.test.tsx
import { render } from '@testing-library/react';
import { MyComponent } from './MyComponent';

test('renders correctly', () => {
  const { getByText } = render(<MyComponent />);
  expect(getByText('...')).toBeInTheDocument();
});
```

### Update Dependencies

```bash
# Check for updates
npm outdated

# Update all dependencies
npm update

# Update specific package
npm update package-name

# Update to latest (breaking changes)
npm install package-name@latest
```

## Troubleshooting

### Port already in use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Database connection errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Redis connection errors

```bash
# Check Redis is running
redis-cli ping

# Restart Redis
sudo systemctl restart redis
```

## Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [React Documentation](https://react.dev/)
- [Express Documentation](https://expressjs.com/)
- [Socket.io Documentation](https://socket.io/docs/)
