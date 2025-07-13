#!/bin/bash
# Script to restore MoneyDiary PostgreSQL database from backup

# Check if backup file is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

BACKUP_FILE="$1"
CONTAINER_NAME="moneydiary-db"
DB_NAME="moneydiary"
DB_USER="moneydiary"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

# Confirm restoration
read -p "This will overwrite the existing database. Are you sure? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Restoration cancelled."
  exit 0
fi

# Restore backup
echo "Restoring backup to $DB_NAME database..."
gunzip -c "$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME

# Check if restoration was successful
if [ $? -eq 0 ]; then
  echo "Database successfully restored from: $BACKUP_FILE"
else
  echo "Restoration failed!"
  exit 1
fi
