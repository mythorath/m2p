#!/bin/bash
# M2P Health Check Script

set -e

# Configuration
API_URL="${API_URL:-http://localhost:5000}"
ALERT_EMAIL="${ALERT_EMAIL:-admin@m2p.example.com}"
LOG_FILE="${LOG_FILE:-/var/log/m2p/health-check.log}"

# Create log directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local subject="$1"
    local message="$2"

    log "ALERT: $subject"

    # Send email if configured
    if command -v mail &> /dev/null && [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "[M2P] $subject" "$ALERT_EMAIL"
    fi

    # Could also send to Slack, Discord, etc.
}

# Check API health
check_api() {
    log "Checking API health..."

    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" --max-time 10)

    if [ "$RESPONSE" -eq 200 ]; then
        log "✓ API is healthy (HTTP $RESPONSE)"
        return 0
    else
        log "✗ API health check failed (HTTP $RESPONSE)"
        send_alert "API Health Check Failed" "API returned HTTP $RESPONSE"
        return 1
    fi
}

# Check database connection
check_database() {
    log "Checking database connection..."

    RESPONSE=$(curl -s "$API_URL/health/db" --max-time 10)
    STATUS=$(echo "$RESPONSE" | jq -r '.database' 2>/dev/null || echo "error")

    if [ "$STATUS" == "connected" ]; then
        log "✓ Database is connected"
        return 0
    else
        log "✗ Database connection failed"
        send_alert "Database Connection Failed" "Database health check failed"
        return 1
    fi
}

# Check Redis connection
check_redis() {
    log "Checking Redis connection..."

    RESPONSE=$(curl -s "$API_URL/health/redis" --max-time 10)
    STATUS=$(echo "$RESPONSE" | jq -r '.redis' 2>/dev/null || echo "error")

    if [ "$STATUS" == "connected" ]; then
        log "✓ Redis is connected"
        return 0
    else
        log "✗ Redis connection failed"
        send_alert "Redis Connection Failed" "Redis health check failed"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."

    USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$USAGE" -lt 80 ]; then
        log "✓ Disk space OK ($USAGE% used)"
        return 0
    elif [ "$USAGE" -lt 90 ]; then
        log "⚠ Disk space warning ($USAGE% used)"
        send_alert "Disk Space Warning" "Disk usage is at $USAGE%"
        return 0
    else
        log "✗ Disk space critical ($USAGE% used)"
        send_alert "Disk Space Critical" "Disk usage is at $USAGE%"
        return 1
    fi
}

# Check memory usage
check_memory() {
    log "Checking memory usage..."

    USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$USAGE" -lt 80 ]; then
        log "✓ Memory OK ($USAGE% used)"
        return 0
    elif [ "$USAGE" -lt 90 ]; then
        log "⚠ Memory warning ($USAGE% used)"
        send_alert "Memory Warning" "Memory usage is at $USAGE%"
        return 0
    else
        log "✗ Memory critical ($USAGE% used)"
        send_alert "Memory Critical" "Memory usage is at $USAGE%"
        return 1
    fi
}

# Main health check
main() {
    log "=========================================="
    log "Starting M2P health check"
    log "=========================================="

    FAILED=0

    check_api || FAILED=$((FAILED + 1))
    check_database || FAILED=$((FAILED + 1))
    check_redis || FAILED=$((FAILED + 1))
    check_disk_space || FAILED=$((FAILED + 1))
    check_memory || FAILED=$((FAILED + 1))

    log "=========================================="
    if [ $FAILED -eq 0 ]; then
        log "✓ All health checks passed"
    else
        log "✗ $FAILED health check(s) failed"
    fi
    log "=========================================="

    exit $FAILED
}

main
