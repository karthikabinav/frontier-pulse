# aifrontierpulse

aifrontierpulse is a local-first research intelligence system that ingests frontier AI artifacts, extracts structured alpha, tracks hypothesis evolution, and supports human-in-the-loop weekly publication.

## V1 Status

V1 backend and frontend are implemented with:
- Multi-source ingestion connectors (arXiv, OpenReview, RSS-based sources)
- Chunking and alpha card generation pipeline
- Hypothesis and cluster synthesis
- Versioned weekly briefs and memory entries
- QA checklist and export generation (Twitter thread, LinkedIn, markdown)
- Hotkey-enabled review UI

## Quick Start (Reproducible ≤20 min path)

This path reproduces the full local stack and validates the experiment-plan generator in ~15–20 minutes on a typical laptop.

### 1. Start database

```bash
cd backend
cp .env.example .env
docker compose up -d db
```

### 2. Start backend (migration-first)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Use dashboard

- Open `http://localhost:5174`
- Run workflow and review hypotheses/clusters/brief
- Save brief and generate exports to clipboard

## One-command Docker stack (optional)

```bash
docker compose -f docker-compose.app.yml up --build
```

This launches Postgres+pgvector, backend API, and frontend UI.

## New: Experiment Plan Generator (v0)

Frontier Pulse now includes a backend script to convert structured hypothesis specs into execution-ready experiment plans.

- Script: `backend/scripts/generate_experiment_plan.py`
- Inputs: hypothesis JSON
- Outputs: Markdown + JSON plan artifacts

Quick run:

```bash
cd backend
python3 scripts/generate_experiment_plan.py \
  --input artifacts/plans/sample_hypotheses.json \
  --output-md artifacts/plans/sample_experiment_plan.md \
  --output-json artifacts/plans/sample_experiment_plan.json
```

Validation/failure-path run (writes explicit mitigation artifacts on error):

```bash
cd backend
python3 scripts/generate_experiment_plan.py \
  --input artifacts/plans/invalid_hypotheses.json \
  --output-md artifacts/plans/invalid_experiment_plan.md \
  --output-json artifacts/plans/invalid_experiment_plan.json || true

ls -1 artifacts/plans/*failure_analysis.*
```

### Repro checklist (<=20 min)

1. Bring up DB + backend + frontend using Quick Start steps.
2. Run sample plan generation command; verify both `.md` and `.json` artifacts are produced.
3. Run failure-path command; verify `_failure_analysis.md` and `_failure_analysis.json` are produced with mitigation notes.
4. Open UI (`http://localhost:5174`) to verify end-to-end local stack.

## Limitations & Safety

- **Generator is template-driven**: it does not execute experiments or validate scientific truth claims.
- **Input quality is critical**: schema validation catches format/type issues, not conceptual flaws in hypotheses.
- **Failure artifacts are advisory**: mitigation notes are operational guidance, not security/compliance guarantees.
- **Human review required**: generated plans should be reviewed before any compute spend, publication, or policy-sensitive use.
- **No autonomous external actions**: this repo does not grant implicit permission for public posting, data sharing, or model deployment.

## Documentation

- Decisions: `DECISIONS.md`
- Tracker: `PROJECT_TRACKER.md`
- QA checklist: `docs/QA_CHECKLIST.md`
- V1 scope: `docs/V1_SCOPE.md`
- Deployment readiness: `docs/deployment/DEPLOYMENT_READINESS.md`
- Build in public: `BLOG_WORKFLOW.md`
