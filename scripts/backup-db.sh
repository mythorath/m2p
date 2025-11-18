#!/bin/bash
# M2P Database Backup Script

set -e

# Configuration
DB_NAME="${DB_NAME:-m2p_db}"
DB_USER="${DB_USER:-m2p_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backup/m2p}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
RETENTION_WEEKS="${RETENTION_WEEKS:-4}"

# Backup type (daily or weekly)
BACKUP_TYPE="${1:-daily}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
if [ "$BACKUP_TYPE" == "full" ]; then
    BACKUP_FILE="$BACKUP_DIR/m2p-db-full-$TIMESTAMP.sql.gz"
else
    BACKUP_FILE="$BACKUP_DIR/m2p-db-$TIMESTAMP.sql.gz"
fi

echo "Starting M2P database backup..."
echo "Backup file: $BACKUP_FILE"

# Perform backup
if [ "$BACKUP_TYPE" == "full" ]; then
    echo "Performing full backup..."
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -F c -b -v -f "$BACKUP_FILE" "$DB_NAME"
else
    echo "Performing regular backup..."
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"
fi

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "✓ Backup completed successfully"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "  Size: $BACKUP_SIZE"
else
    echo "✗ Backup failed!"
    exit 1
fi

# Cleanup old backups
echo "Cleaning up old backups..."

# Remove daily backups older than retention period
find "$BACKUP_DIR" -name "m2p-db-*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "✓ Removed daily backups older than $RETENTION_DAYS days"

# Remove full backups older than retention period
find "$BACKUP_DIR" -name "m2p-db-full-*.sql.gz" -type f -mtime +$((RETENTION_WEEKS * 7)) -delete
echo "✓ Removed weekly backups older than $RETENTION_WEEKS weeks"

# Optional: Upload to S3
if [ -n "$AWS_S3_BUCKET" ]; then
    echo "Uploading backup to S3..."
    aws s3 cp "$BACKUP_FILE" "s3://$AWS_S3_BUCKET/m2p-backups/" --storage-class STANDARD_IA
    if [ $? -eq 0 ]; then
        echo "✓ Backup uploaded to S3"
    else
        echo "✗ S3 upload failed"
    fi
fi

# List recent backups
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -n 5

echo ""
echo "Backup complete!"
