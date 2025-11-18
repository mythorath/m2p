# Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Application Deployment](#application-deployment)
- [Docker Deployment](#docker-deployment)
- [Nginx Configuration](#nginx-configuration)
- [SSL Setup](#ssl-setup)
- [Systemd Services](#systemd-services)
- [Monitoring Setup](#monitoring-setup)
- [Backup Strategy](#backup-strategy)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 50GB SSD
- OS: Ubuntu 20.04 LTS or later

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 100GB+ SSD
- OS: Ubuntu 22.04 LTS

### Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL 13+
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose

# Install PM2 for process management
sudo npm install -g pm2

# Install Python 3.9+ (for admin tools)
sudo apt install -y python3 python3-pip
```

## Environment Setup

### 1. Create System User

```bash
# Create dedicated user for M2P
sudo useradd -m -s /bin/bash m2p
sudo usermod -aG sudo m2p

# Switch to m2p user
sudo su - m2p
```

### 2. Clone Repository

```bash
cd /home/m2p
git clone https://github.com/yourusername/m2p.git
cd m2p
```

### 3. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:

```bash
# Application
NODE_ENV=production
PORT=5000
API_URL=https://api.yourdomain.com

# Database
DATABASE_URL=postgresql://m2p_user:secure_password@localhost:5432/m2p_db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# JWT
JWT_SECRET=your_very_secure_jwt_secret_min_32_chars
JWT_EXPIRY=86400

# Wallet Authentication
WALLET_CHALLENGE_EXPIRY=300

# Rate Limiting
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX_REQUESTS=1000

# CORS
CORS_ORIGIN=https://yourdomain.com

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/m2p/app.log
```

## Database Setup

### 1. Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE m2p_db;
CREATE USER m2p_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE m2p_db TO m2p_user;

-- Enable extensions
\c m2p_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Exit psql
\q
```

### 2. Configure PostgreSQL

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Recommended settings:
```
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Run Database Migrations

```bash
cd /home/m2p/m2p/server
npm install
npm run db:migrate
npm run db:seed  # Optional: seed with initial data
```

### 4. Setup Redis

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf
```

Key settings:
```
bind 127.0.0.1
protected-mode yes
port 6379
requirepass your_redis_password
maxmemory 512mb
maxmemory-policy allkeys-lru
```

```bash
# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

## Application Deployment

### Option 1: Manual Deployment with PM2

#### 1. Build Applications

```bash
# Build backend
cd /home/m2p/m2p/server
npm install --production
npm run build

# Build frontend
cd /home/m2p/m2p/client
npm install --production
npm run build
```

#### 2. Configure PM2

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [
    {
      name: 'm2p-server',
      script: './dist/index.js',
      cwd: '/home/m2p/m2p/server',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/var/log/m2p/server-error.log',
      out_file: '/var/log/m2p/server-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      max_memory_restart: '1G'
    }
  ]
};
```

#### 3. Start with PM2

```bash
# Create log directory
sudo mkdir -p /var/log/m2p
sudo chown m2p:m2p /var/log/m2p

# Start applications
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Run the command it outputs
```

### Option 2: Docker Deployment (Recommended)

See [Docker Deployment](#docker-deployment) section below.

## Docker Deployment

### 1. Build Docker Images

```bash
cd /home/m2p/m2p

# Build server image
docker build -f deploy/docker/Dockerfile.server -t m2p-server:latest .

# Build client image
docker build -f deploy/docker/Dockerfile.client -t m2p-client:latest .
```

### 2. Use Docker Compose

```bash
cd deploy/docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Docker Compose Configuration

See `deploy/docker/docker-compose.yml` for the complete configuration.

Key services:
- **nginx**: Reverse proxy and load balancer
- **app-server-1, app-server-2**: Application servers
- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **prometheus**: Metrics collection
- **grafana**: Monitoring dashboards

## Nginx Configuration

### 1. Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

### 2. Configure Nginx

```bash
# Copy nginx configuration
sudo cp /home/m2p/m2p/deploy/nginx/nginx.conf /etc/nginx/sites-available/m2p

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/m2p /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 3. Enable HTTP/2 and Optimize

Add to nginx configuration:
```nginx
# Enable HTTP/2
listen 443 ssl http2;

# SSL optimization
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## SSL Setup

### Manual SSL Certificate Setup

If not using Let's Encrypt:

```bash
# Generate self-signed certificate (for testing only)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/m2p-selfsigned.key \
  -out /etc/ssl/certs/m2p-selfsigned.crt

# Or copy your SSL certificates
sudo cp your-cert.crt /etc/ssl/certs/m2p.crt
sudo cp your-key.key /etc/ssl/private/m2p.key

# Set proper permissions
sudo chmod 600 /etc/ssl/private/m2p.key
```

### SSL Security Best Practices

```nginx
# Modern SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Systemd Services

### Create Service Files

#### M2P Server Service

```bash
sudo nano /etc/systemd/system/m2p-server.service
```

```ini
[Unit]
Description=M2P Game Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=m2p
WorkingDirectory=/home/m2p/m2p/server
ExecStart=/usr/bin/node dist/index.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=m2p-server
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

#### M2P Worker Service (for background jobs)

```bash
sudo nano /etc/systemd/system/m2p-worker.service
```

```ini
[Unit]
Description=M2P Background Worker
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=m2p
WorkingDirectory=/home/m2p/m2p/server
ExecStart=/usr/bin/node dist/worker.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=m2p-worker
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable m2p-server.service
sudo systemctl enable m2p-worker.service

# Start services
sudo systemctl start m2p-server.service
sudo systemctl start m2p-worker.service

# Check status
sudo systemctl status m2p-server.service
sudo systemctl status m2p-worker.service

# View logs
sudo journalctl -u m2p-server.service -f
```

## Monitoring Setup

### 1. Prometheus Configuration

```bash
# Create Prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# Create directories
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

# Copy configuration
sudo cp /home/m2p/m2p/deploy/monitoring/prometheus.yml /etc/prometheus/

# Set ownership
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
```

### 2. Grafana Setup

```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access Grafana at http://localhost:3000
# Default credentials: admin/admin
```

### 3. Import Grafana Dashboard

```bash
# Import the M2P dashboard
# Copy deploy/monitoring/grafana-dashboard.json
# In Grafana UI: Dashboards > Import > Upload JSON
```

### 4. Setup Alerts

Configure Prometheus alert rules in `/etc/prometheus/alert.rules.yml`:

```yaml
groups:
  - name: m2p_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseDown
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
```

## Backup Strategy

### 1. Database Backups

#### Automated Daily Backups

```bash
# Create backup script
sudo cp /home/m2p/m2p/scripts/backup-db.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup-db.sh

# Setup cron job
crontab -e
```

Add:
```cron
# Daily database backup at 2 AM
0 2 * * * /usr/local/bin/backup-db.sh

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /usr/local/bin/backup-db.sh --full
```

#### Manual Backup

```bash
# Backup database
/usr/local/bin/backup-db.sh

# Restore database
/usr/local/bin/restore-db.sh /path/to/backup.sql
```

### 2. Application Backups

```bash
# Backup application files
sudo tar -czf /backup/m2p-app-$(date +%Y%m%d).tar.gz /home/m2p/m2p

# Backup configuration
sudo tar -czf /backup/m2p-config-$(date +%Y%m%d).tar.gz \
  /etc/nginx/sites-available/m2p \
  /home/m2p/m2p/.env \
  /etc/systemd/system/m2p-*.service
```

### 3. Backup Retention

```bash
# Keep last 7 daily backups
find /backup -name "m2p-db-*.sql" -mtime +7 -delete

# Keep last 4 weekly backups
find /backup -name "m2p-db-full-*.sql" -mtime +28 -delete
```

### 4. Off-site Backups

```bash
# Sync to S3
aws s3 sync /backup s3://your-backup-bucket/m2p/

# Or use rsync to remote server
rsync -avz /backup/ user@backup-server:/backups/m2p/
```

## Health Checks

### Application Health Endpoint

The application provides a health check endpoint:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00Z",
  "uptime": 86400,
  "database": "connected",
  "redis": "connected"
}
```

### Automated Health Monitoring

```bash
# Create health check script
sudo nano /usr/local/bin/health-check.sh
```

```bash
#!/bin/bash
HEALTH_URL="http://localhost:5000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
  echo "Health check failed! Response: $RESPONSE"
  # Send alert (email, Slack, etc.)
  # Optionally restart service
  # sudo systemctl restart m2p-server
fi
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/health-check.sh

# Add to cron (every 5 minutes)
*/5 * * * * /usr/local/bin/health-check.sh
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_players_last_active ON players(last_active DESC);
CREATE INDEX CONCURRENTLY idx_pool_members_pool_player ON pool_members(pool_id, player_id);

-- Analyze tables
ANALYZE players;
ANALYZE pools;
ANALYZE pool_members;

-- Vacuum tables
VACUUM ANALYZE;
```

### 2. Redis Caching

Configure cache warming:

```bash
# Add to startup script
redis-cli SET "cache:pools" "$(curl http://localhost:5000/api/v1/pools)"
```

### 3. Nginx Caching

Add to nginx configuration:

```nginx
# Cache static assets
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

# API response caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;
proxy_cache api_cache;
proxy_cache_valid 200 5m;
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Prometheus (from monitoring server only)
sudo ufw allow from monitoring_server_ip to any port 9090

# Verify rules
sudo ufw status
```

### 2. Fail2Ban

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Configure for nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
# Restart Fail2Ban
sudo systemctl restart fail2ban
```

### 3. Regular Updates

```bash
# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Scaling

### Horizontal Scaling

#### Add Application Server

1. Deploy application to new server
2. Update Nginx upstream configuration:

```nginx
upstream m2p_backend {
  least_conn;
  server app1.internal:5000 weight=1;
  server app2.internal:5000 weight=1;
  server app3.internal:5000 weight=1;  # New server
}
```

3. Reload Nginx: `sudo systemctl reload nginx`

#### Database Replication

Setup PostgreSQL read replicas for scalability:

```bash
# On primary server
# Edit postgresql.conf
wal_level = replica
max_wal_senders = 3

# Create replication user
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'password';
```

## Troubleshooting

### Common Issues

#### Application won't start

```bash
# Check logs
sudo journalctl -u m2p-server -n 100

# Check if port is in use
sudo lsof -i :5000

# Verify environment variables
pm2 env 0
```

#### Database connection errors

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U m2p_user -d m2p_db -h localhost

# Check connection limits
SELECT count(*) FROM pg_stat_activity;
```

#### High memory usage

```bash
# Check memory usage
free -h
pm2 monit

# Restart application
pm2 restart all

# Clear cache
redis-cli FLUSHDB
```

### Rollback Procedure

```bash
# Stop current version
pm2 stop all

# Restore previous version
cd /home/m2p/m2p
git checkout previous-version-tag
npm install
npm run build

# Rollback database (if needed)
npm run db:rollback

# Restart
pm2 restart all
```

## Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] SSL certificate installed and valid
- [ ] Database backups configured
- [ ] Monitoring dashboards accessible
- [ ] Health checks passing
- [ ] Logs rotating properly
- [ ] Firewall rules configured
- [ ] DNS records pointing correctly
- [ ] Rate limiting working
- [ ] WebSocket connections working
- [ ] Email notifications configured (if applicable)
- [ ] Documentation updated

## Maintenance Windows

Schedule regular maintenance:

```bash
# Monthly maintenance - First Sunday 2-4 AM
# 1. Update system packages
# 2. Update Node.js packages
# 3. Database optimization
# 4. Review logs and metrics
# 5. Test backups
# 6. Security audit
```

## Support

For deployment issues:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review logs in `/var/log/m2p/`
- Contact DevOps team: devops@m2p.example.com
