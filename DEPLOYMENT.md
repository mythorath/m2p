# M2P Wallet Verification System - Deployment Guide

This guide covers production deployment of the M2P Wallet Verification System.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8 or higher
- Nginx (optional, for reverse proxy)
- PostgreSQL or MySQL (recommended for production)
- SSL certificate (Let's Encrypt recommended)
- Sudo/root access

## Production Deployment

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib

# Create application user
sudo useradd -m -s /bin/bash m2p

# Create application directory
sudo mkdir -p /opt/m2p
sudo chown m2p:m2p /opt/m2p
```

### 2. Clone Repository

```bash
# Switch to m2p user
sudo su - m2p

# Clone repository
cd /opt/m2p
git clone <repository-url> .

# Or copy files
# Copy your application files to /opt/m2p
```

### 3. Install Application

```bash
# Run setup script
./setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. PostgreSQL Database Setup

```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb m2p
createuser m2p_user
psql -c "ALTER USER m2p_user WITH PASSWORD 'secure_password_here';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE m2p TO m2p_user;"

# Exit postgres user
exit
```

### 5. Configure Environment

```bash
# Edit .env file
sudo nano /opt/m2p/.env
```

```bash
# Production .env configuration
DATABASE_URL=postgresql://m2p_user:secure_password_here@localhost/m2p
DEV_WALLET_ADDRESS=your_actual_dev_wallet_address
ADMIN_API_KEY=generate_secure_random_key_here
SECRET_KEY=generate_secure_random_key_here
VERIFICATION_TIMEOUT_HOURS=24
VERIFICATION_CHECK_INTERVAL_MINUTES=5
MIN_CONFIRMATIONS=6
AP_REFUND_MULTIPLIER=100
PORT=5000
LOG_LEVEL=INFO
LOG_FILE=/opt/m2p/logs/verifier.log
```

**Generate secure keys:**
```bash
# Generate random keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Initialize Database

```bash
# As m2p user
cd /opt/m2p
source venv/bin/activate
python init_db.py
```

### 7. Install Systemd Service

```bash
# Copy service file
sudo cp /opt/m2p/m2p-verifier.service /etc/systemd/system/

# Edit service file if needed
sudo nano /etc/systemd/system/m2p-verifier.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable m2p-verifier

# Start service
sudo systemctl start m2p-verifier

# Check status
sudo systemctl status m2p-verifier
```

### 8. Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/m2p
```

```nginx
# /etc/nginx/sites-available/m2p
upstream m2p_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/m2p_access.log;
    error_log /var/log/nginx/m2p_error.log;

    # WebSocket support
    location /socket.io {
        proxy_pass http://m2p_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location / {
        proxy_pass http://m2p_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-API-Key" always;

        # Handle preflight requests
        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # Admin endpoints - restrict by IP
    location /admin {
        # Allow only specific IPs
        allow 192.168.1.0/24;  # Your office network
        deny all;

        proxy_pass http://m2p_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/m2p /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

## Monitoring and Logging

### View Application Logs

```bash
# View service logs
sudo journalctl -u m2p-verifier -f

# View application log file
tail -f /opt/m2p/logs/verifier.log

# View Nginx logs
tail -f /var/log/nginx/m2p_access.log
tail -f /var/log/nginx/m2p_error.log
```

### Log Rotation

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/m2p
```

```
/opt/m2p/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 m2p m2p
    sharedscripts
    postrotate
        systemctl reload m2p-verifier > /dev/null 2>&1 || true
    endscript
}
```

### System Monitoring

Consider installing monitoring tools:

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Optional: Install Prometheus node exporter
# Optional: Set up Grafana dashboards
# Optional: Configure alerting (PagerDuty, Slack, etc.)
```

## Maintenance

### Update Application

```bash
# Switch to m2p user
sudo su - m2p
cd /opt/m2p

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install updated dependencies
pip install -r requirements.txt

# Run database migrations (if any)
# python migrate.py

# Exit m2p user
exit

# Restart service
sudo systemctl restart m2p-verifier

# Check status
sudo systemctl status m2p-verifier
```

### Database Backup

```bash
# Create backup script
sudo nano /opt/m2p/backup.sh
```

```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/opt/m2p/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="m2p"
DB_USER="m2p_user"

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/m2p_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "m2p_*.sql.gz" -mtime +30 -delete

echo "Backup completed: m2p_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /opt/m2p/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add line:
# 0 2 * * * /opt/m2p/backup.sh
```

### Performance Tuning

#### PostgreSQL Optimization

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/*/main/postgresql.conf
```

```
# Tune for your server specs
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

#### Application Optimization

```bash
# Use Gunicorn for production
pip install gunicorn gevent gevent-websocket

# Update systemd service
ExecStart=/opt/m2p/venv/bin/gunicorn \
    --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /opt/m2p/logs/access.log \
    --error-logfile /opt/m2p/logs/error.log \
    server.app:app
```

## Security Hardening

### Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH (be careful!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Fail2Ban

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Configure for Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban
```

### Regular Security Updates

```bash
# Enable automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status m2p-verifier

# Check logs
sudo journalctl -u m2p-verifier -n 100

# Check permissions
ls -la /opt/m2p
sudo chown -R m2p:m2p /opt/m2p

# Check Python errors
sudo su - m2p
cd /opt/m2p
source venv/bin/activate
python -m server.app
```

### Database Connection Issues

```bash
# Test database connection
sudo su - m2p
cd /opt/m2p
source venv/bin/activate
python -c "from server.config import DATABASE_URL; from sqlalchemy import create_engine; engine = create_engine(DATABASE_URL); print('Connection successful')"
```

### WebSocket Not Working

```bash
# Check Nginx configuration
sudo nginx -t

# Ensure WebSocket headers are set correctly
# Check browser console for WebSocket errors
# Verify firewall allows WebSocket connections
```

## Production Checklist

- [ ] PostgreSQL database configured
- [ ] Secure passwords and API keys generated
- [ ] `.env` file configured with production values
- [ ] Database initialized
- [ ] Systemd service installed and running
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Log rotation configured
- [ ] Database backups scheduled
- [ ] Monitoring set up
- [ ] Admin endpoints IP-restricted
- [ ] Security headers enabled
- [ ] fail2ban configured
- [ ] Automatic updates enabled
- [ ] Documentation updated with production URLs

## Support

For deployment issues:
- Check logs first: `sudo journalctl -u m2p-verifier -f`
- Review [README.md](README.md) troubleshooting section
- Open GitHub issue with relevant logs
