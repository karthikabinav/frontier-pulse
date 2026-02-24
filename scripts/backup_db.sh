#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"

mkdir -p "$BACKUP_DIR"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set"
  exit 1
fi

pg_dump "$DATABASE_URL" > "$BACKUP_DIR/aifrontierpulse_${TIMESTAMP}.sql"

find "$BACKUP_DIR" -name 'aifrontierpulse_*.sql' -type f -mtime +"$RETENTION_DAYS" -delete

echo "Backup complete: $BACKUP_DIR/aifrontierpulse_${TIMESTAMP}.sql"
