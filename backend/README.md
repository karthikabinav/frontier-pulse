# aifrontierpulse Backend

## Run (native)

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Preferred DB bootstrap (migrations)
alembic upgrade head

uvicorn app.main:app --reload
```

## Run DB (Docker)

```bash
docker compose up -d db
```

## Migration modes

- `DB_INIT_MODE=migrate` (default): assumes schema is managed by Alembic.
- `DB_INIT_MODE=create_all`: dev-only fallback to SQLAlchemy `create_all`.

## API

- `GET /api/v1/health`
- `GET /api/v1/papers`
- `GET /api/v1/papers/{paper_id}`
- `POST /api/v1/workflows/weekly-run`
- `GET /api/v1/workflows/ingestion-policy`
- `GET /api/v1/workflows/inference-policy`
- `GET /api/v1/workflows/project-policy`
- `GET /api/v1/hypotheses`
- `GET /api/v1/clusters`
- `GET /api/v1/briefs/latest`
- `POST /api/v1/briefs/update`
- `POST /api/v1/exports/generate`
- `GET /api/v1/qa/checklist`

## Scheduler

Nightly scheduler runs in-process when `SCHEDULER_MODE=in_process`.
Defaults to `2:00 AM` in `America/Los_Angeles`.

For production, prefer `SCHEDULER_MODE=off` in API replicas and run scheduler as a single dedicated worker process.

## Backups

```bash
source .env
BACKUP_RETENTION_DAYS=7 ../scripts/backup_db.sh
```
