# Security Guide

## Authentication & Authorization

### Wallet-Based Authentication
- Use signature verification for wallet authentication
- Never store private keys
- Implement nonce-based challenge system
- Set expiration on authentication challenges (5 minutes)
- Use JWT tokens with proper expiration (24 hours)

### JWT Security
```typescript
// Use strong secret (min 32 characters)
JWT_SECRET=your_very_secure_secret_min_32_characters

// Set appropriate expiration
JWT_EXPIRY=86400  // 24 hours

// Rotate secrets periodically
// Implement token blacklist for revoked tokens
```

## Input Validation

### Server-Side Validation
Always validate all inputs:
```typescript
import { z } from 'zod';

const walletSchema = z.object({
  wallet_address: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
});

// Validate
const result = walletSchema.safeParse(req.body);
if (!result.success) {
  return res.status(400).json({ error: result.error });
}
```

### SQL Injection Prevention
- Use Prisma ORM (parameterized queries)
- Never concatenate user input into queries
- Use prepared statements if raw SQL is needed

### XSS Prevention
- Sanitize all user-generated content
- Use Content Security Policy headers
- Escape HTML output
- Use React's built-in XSS protection

```typescript
// Content Security Policy
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));
```

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// API rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
});

// Auth rate limiting (stricter)
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 attempts per 15 minutes
  skipSuccessfulRequests: true,
});

app.use('/api/v1/', apiLimiter);
app.use('/api/v1/auth/', authLimiter);
```

## CSRF Protection

```typescript
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

// Apply to state-changing routes
app.post('/api/v1/pools', csrfProtection, createPool);
```

## Data Protection

### Sensitive Data
- Never log sensitive information (passwords, private keys, tokens)
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper access controls

### Database Security
```sql
-- Create dedicated database user with limited permissions
CREATE USER m2p_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO m2p_user;
-- Do NOT grant DROP, ALTER, or other DDL permissions

-- Enable row-level security
ALTER TABLE players ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY player_policy ON players
  FOR ALL
  USING (wallet_address = current_user_wallet());
```

## Environment Variables

Never commit `.env` files:
```bash
# .gitignore
.env
.env.local
.env.production
```

Use environment-specific files:
```bash
.env.example         # Template (committed)
.env.development     # Local dev (not committed)
.env.production      # Production (not committed)
```

## Security Headers

```typescript
import helmet from 'helmet';

app.use(helmet());

// Additional headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});
```

## Dependency Security

```bash
# Regular security audits
npm audit

# Fix vulnerabilities
npm audit fix

# Check for known vulnerabilities
npm install -g snyk
snyk test
```

## WebSocket Security

```typescript
// Authenticate WebSocket connections
io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth.token;
    const user = await verifyToken(token);
    socket.user = user;
    next();
  } catch (error) {
    next(new Error('Authentication error'));
  }
});

// Validate all incoming messages
socket.on('submit_share', async (data) => {
  const validated = shareSchema.parse(data);
  // Process validated data
});

// Rate limit WebSocket messages
const messageRateLimiter = new Map();
socket.on('message', (data) => {
  const count = messageRateLimiter.get(socket.id) || 0;
  if (count > 100) {
    socket.disconnect();
    return;
  }
  messageRateLimiter.set(socket.id, count + 1);
});
```

## Secure File Uploads

```typescript
import multer from 'multer';

const upload = multer({
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB max
  },
  fileFilter: (req, file, cb) => {
    // Allow only specific file types
    const allowedTypes = ['image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.mimetype)) {
      cb(new Error('Invalid file type'));
      return;
    }
    cb(null, true);
  },
});
```

## Logging & Monitoring

```typescript
// Log security events
logger.warn('Failed login attempt', {
  wallet: req.body.wallet_address,
  ip: req.ip,
  timestamp: new Date(),
});

// Monitor for suspicious activity
if (failedAttempts > 5) {
  logger.alert('Multiple failed login attempts', { wallet, ip });
  // Implement lockout or CAPTCHA
}
```

## Incident Response

1. **Detection**: Monitor logs and alerts
2. **Containment**: Isolate affected systems
3. **Investigation**: Analyze logs and determine scope
4. **Remediation**: Patch vulnerabilities
5. **Recovery**: Restore from clean backups
6. **Post-Incident**: Document and improve security

## Security Checklist

- [ ] All inputs validated and sanitized
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (CSP, output escaping)
- [ ] CSRF protection on state-changing endpoints
- [ ] Rate limiting implemented
- [ ] Authentication properly implemented
- [ ] Authorization checks on all protected routes
- [ ] Sensitive data encrypted
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Dependencies regularly updated
- [ ] Security audit performed
- [ ] Logging and monitoring active
- [ ] Backup strategy in place
- [ ] Incident response plan documented

## Reporting Security Issues

Report security vulnerabilities to: security@m2p.example.com

Do not open public issues for security vulnerabilities.
