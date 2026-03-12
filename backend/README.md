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
- `GET /api/v1/diagnostics`
- `GET /api/v1/papers`
- `GET /api/v1/papers/{paper_id}`
- `POST /api/v1/workflows/weekly-run`
- `GET /api/v1/workflows/ingestion-policy`
- `GET /api/v1/workflows/inference-policy`
- `GET /api/v1/workflows/project-policy`
- `GET /api/v1/hypotheses`
- `GET /api/v1/memory` (supports `query`, `recent_weeks`, `week_key`, `memory_type`, `limit`)
- `GET /api/v1/clusters`
- `GET /api/v1/briefs/latest`
- `POST /api/v1/briefs/update`
- `POST /api/v1/exports/generate`
- `GET /api/v1/qa/checklist`

## Experiment plan generator (v0)

Generate execution-ready experiment plans from structured hypothesis specs.

Script:
- `backend/scripts/generate_experiment_plan.py`

Usage:

```bash
cd backend
python3 scripts/generate_experiment_plan.py \
  --input artifacts/plans/sample_hypotheses.json \
  --output-md artifacts/plans/sample_experiment_plan.md \
  --output-json artifacts/plans/sample_experiment_plan.json
```

Outputs:
- `backend/artifacts/plans/sample_experiment_plan.md`
- `backend/artifacts/plans/sample_experiment_plan.json`

## Eval slice (baseline vs current)

Executable benchmark fixture + scoring script for plan quality/regression.

Inputs:
- `backend/artifacts/evals/hypothesis_eval_fixture.json` (4 valid hypotheses + 1 edge/failure case)

Script:
- `backend/scripts/score_experiment_plan_eval.py`

Usage:

```bash
cd backend
python3 scripts/score_experiment_plan_eval.py --runs 3
```

Outputs:
- `backend/artifacts/evals/results_latest.json`
- `backend/artifacts/evals/results_latest.md`

## Scheduler

Nightly scheduler runs in-process when `SCHEDULER_MODE=in_process`.
Defaults to `2:00 AM` in `America/Los_Angeles`.

For production, prefer `SCHEDULER_MODE=off` in API replicas and run scheduler as a single dedicated worker process.

## Verification artifacts

Each weekly run writes arXiv coverage verification artifacts:
- `artifacts/verification/<week_key>.json`
- `artifacts/verification/<week_key>.md`

Includes discovered IDs, processed IDs, full-text coverage, abstract-only fallbacks, and failed count.

## Backups

```bash
source .env
BACKUP_RETENTION_DAYS=7 ../scripts/backup_db.sh
```
