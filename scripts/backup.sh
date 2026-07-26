#!/usr/bin/env bash
# Nightly Postgres backup for both environments. Keeps the last 14 backups
# per environment (older ones are deleted by count, not by age, so it
# still holds 14 even if the schedule is ever irregular).
#
# Usage: scripts/backup.sh
# Intended to run from cron, e.g.:
#   0 2 * * * /root/bueza-pets/scripts/backup.sh >> /var/log/bueza-pets-backup.log 2>&1
set -euo pipefail

BACKUP_ROOT="/root/bueza-pets-backups"
KEEP=14
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

backup_one() {
  local env_name="$1" container="$2" env_file="$3"

  if [ ! -f "$env_file" ]; then
    echo "==> [$env_name] $env_file not found, skipping." >&2
    return
  fi

  local db_user db_name
  db_user=$(grep -m1 '^POSTGRES_USER=' "$env_file" | cut -d= -f2-)
  db_name=$(grep -m1 '^POSTGRES_DB=' "$env_file" | cut -d= -f2-)

  local dir="$BACKUP_ROOT/$env_name"
  mkdir -p "$dir"
  local file="$dir/${db_name}_${TIMESTAMP}.sql.gz"

  echo "==> [$env_name] Backing up $container..."
  docker exec "$container" pg_dump -U "$db_user" "$db_name" | gzip > "$file"
  echo "==> [$env_name] Saved $file ($(du -h "$file" | cut -f1))"

  # Keep only the most recent $KEEP backups for this environment.
  ls -1t "$dir"/*.sql.gz 2>/dev/null | tail -n "+$((KEEP + 1))" | xargs -r rm -f
}

backup_one "production" "bueza-pets-db-prod" "/root/bueza-pets/.env.production"
backup_one "staging" "bueza-pets-db-staging" "/root/bueza-pets-staging/.env.staging"

echo "==> Backup run complete."
