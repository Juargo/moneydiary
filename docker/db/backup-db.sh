#!/bin/bash
# Script to backup MoneyDiary PostgreSQL database

# Configuration
BACKUP_DIR="$(dirname "$0")/backup"
CONTAINER_NAME="moneydiary-db"
DB_NAME="moneydiary"
DB_USER="moneydiary"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/moneydiary_backup_$TIMESTAMP.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup of $DB_NAME database..."
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
  echo "Backup successfully created: $BACKUP_FILE"
  # Optional: Remove backups older than 7 days
  find "$BACKUP_DIR" -name "moneydiary_backup_*.sql.gz" -type f -mtime +7 -delete
else
  echo "Backup failed!"
  exit 1
fi
