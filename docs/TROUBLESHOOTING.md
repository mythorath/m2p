# Troubleshooting Guide

## Common Issues

### Application Won't Start

**Symptom**: Server fails to start or crashes immediately

**Solutions**:
```bash
# Check logs
pm2 logs m2p-server
# or
sudo journalctl -u m2p-server -f

# Common causes:
# 1. Port already in use
lsof -i :5000
kill -9 <PID>

# 2. Environment variables missing
cat .env | grep -v '^#'

# 3. Database connection failed
psql -U m2p_user -d m2p_db -h localhost

# 4. Node modules not installed
cd server && npm install
```

### Database Connection Errors

**Error**: `Error: connect ECONNREFUSED`

**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL

# Check pg_hba.conf for authentication
sudo nano /etc/postgresql/13/main/pg_hba.conf
```

### Redis Connection Errors

**Error**: `Error: Redis connection to localhost:6379 failed`

**Solutions**:
```bash
# Check Redis status
sudo systemctl status redis

# Start Redis
sudo systemctl start redis

# Test connection
redis-cli ping

# Check password
redis-cli -a your_password ping
```

### WebSocket Connection Issues

**Symptom**: Real-time updates not working

**Solutions**:
```bash
# Check WebSocket endpoint
wscat -c ws://localhost:5000

# Check CORS settings
# Ensure CLIENT_URL in .env matches frontend URL

# Check nginx WebSocket configuration
sudo nginx -t
sudo systemctl reload nginx

# Verify WebSocket upgrade headers
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:5000
```

### High Memory Usage

**Symptom**: Application using excessive memory

**Solutions**:
```bash
# Check memory usage
free -h
pm2 monit

# Identify memory leaks
node --inspect server/dist/index.js
# Use Chrome DevTools to take heap snapshots

# Restart application
pm2 restart m2p-server

# Clear Redis cache
redis-cli FLUSHDB

# Increase swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow API Response Times

**Symptom**: API requests taking > 1 second

**Solutions**:
```bash
# Check database queries
# Enable query logging in PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: log_min_duration_statement = 1000

# Analyze slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

# Add missing indexes
CREATE INDEX idx_name ON table_name(column_name);

# Check Redis cache hit rate
redis-cli INFO stats | grep hits

# Monitor API response times
pm2 logs | grep "Response time"
```

### Authentication Failures

**Error**: `Invalid signature` or `Token expired`

**Solutions**:
```bash
# Check JWT secret is set
echo $JWT_SECRET

# Verify wallet signature verification
# Check that challenge hasn't expired

# Clear old sessions
redis-cli KEYS "session:*" | xargs redis-cli DEL

# Check system time is synchronized
timedatectl status
```

### Pool Join Failures

**Error**: `Pool is full` or `Already a member`

**Solutions**:
```sql
-- Check pool capacity
SELECT id, name, max_players, current_players
FROM pools
WHERE id = 1;

-- Check existing membership
SELECT *
FROM pool_members
WHERE player_id = 123 AND pool_id = 1;

-- Fix stuck member count
UPDATE pools
SET current_players = (
  SELECT COUNT(*) FROM pool_members
  WHERE pool_id = pools.id AND is_active = true
)
WHERE id = 1;
```

### Achievement Not Unlocking

**Symptom**: Achievement requirements met but not unlocking

**Solutions**:
```sql
-- Check achievement requirements
SELECT id, name, requirements
FROM achievements
WHERE id = 5;

-- Check player progress
SELECT *
FROM player_achievements
WHERE player_id = 123 AND achievement_id = 5;

-- Manually trigger achievement check
-- Use admin.py script
python3 scripts/admin.py check-achievements --player 123
```

### Frontend Build Errors

**Error**: Build fails with module errors

**Solutions**:
```bash
# Clear node_modules and reinstall
cd client
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist .vite

# Check Node.js version
node -v  # Should be >= 18

# Update dependencies
npm update
```

### Nginx 502 Bad Gateway

**Symptom**: Nginx returns 502 error

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:5000/health

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test nginx configuration
sudo nginx -t

# Check upstream configuration
sudo nano /etc/nginx/sites-available/m2p

# Restart nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues

**Error**: Certificate expired or invalid

**Solutions**:
```bash
# Check certificate expiration
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate chain
sudo openssl s_client -connect yourdomain.com:443 -showcerts
```

### Migration Failures

**Error**: Database migration fails

**Solutions**:
```bash
# Check migration status
npm run db:migrate:status

# Rollback last migration
npm run db:migrate:rollback

# Fix migration file
nano prisma/migrations/XXXXX_migration_name/migration.sql

# Rerun migration
npm run db:migrate

# Force migration (use cautiously)
npm run db:migrate:deploy
```

## Debugging Tips

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=debug

# Restart application
pm2 restart m2p-server
```

### Check Application Health

```bash
# Health check endpoint
curl http://localhost:5000/health

# Database connection
curl http://localhost:5000/health/db

# Redis connection
curl http://localhost:5000/health/redis
```

### Monitor Real-time Logs

```bash
# Application logs
pm2 logs m2p-server --lines 100

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

### Database Debugging

```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Kill stuck queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
AND state = 'idle in transaction'
AND state_change < NOW() - INTERVAL '5 minutes';

-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Performance Issues

### Database Optimization

```sql
-- Vacuum database
VACUUM ANALYZE;

-- Reindex
REINDEX DATABASE m2p_db;

-- Update statistics
ANALYZE;
```

### Cache Optimization

```bash
# Check Redis memory usage
redis-cli INFO memory

# Clear specific keys
redis-cli KEYS "cache:*" | xargs redis-cli DEL

# Set appropriate maxmemory
redis-cli CONFIG SET maxmemory 512mb
```

## Error Codes Reference

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_WALLET` | Invalid wallet address | Check address format (0x...) |
| `SIGNATURE_INVALID` | Signature verification failed | Retry wallet signing |
| `TOKEN_EXPIRED` | JWT token expired | Refresh token or re-authenticate |
| `POOL_FULL` | Pool at capacity | Join different pool |
| `ALREADY_MEMBER` | Already in pool | Leave pool first |
| `INSUFFICIENT_AP` | Not enough AP | Earn more achievements |
| `PLAYER_BANNED` | Account banned | Contact support |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retrying |

## Getting Help

1. **Check Documentation**: Review relevant docs in `docs/`
2. **Search Issues**: Check GitHub issues for similar problems
3. **Check Logs**: Review application and system logs
4. **Community Support**: Ask in Discord/forums
5. **Contact Support**: Email support@m2p.example.com

## Reporting Bugs

When reporting bugs, include:

1. **Description**: What happened vs what you expected
2. **Steps to Reproduce**: How to trigger the bug
3. **Environment**: OS, Node version, browser (if frontend)
4. **Logs**: Relevant error messages and stack traces
5. **Screenshots**: If applicable

Create issue at: https://github.com/yourusername/m2p/issues
