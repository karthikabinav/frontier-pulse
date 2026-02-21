# Frontier Pulse

Frontier Pulse is a local-first research intelligence system that ingests frontier AI artifacts, extracts structured alpha, tracks hypothesis evolution, and supports human-in-the-loop weekly publication.

## V1 Status

V1 backend and frontend are implemented with:
- Multi-source ingestion connectors (arXiv, OpenReview, RSS-based sources)
- Chunking and alpha card generation pipeline
- Hypothesis and cluster synthesis
- Versioned weekly briefs and memory entries
- QA checklist and export generation (Twitter thread, LinkedIn, markdown)
- Hotkey-enabled review UI

## Quick Start

### 1. Start database

```bash
cd backend
cp .env.example .env
docker compose up -d db
```

### 2. Start backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
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

## Documentation

- Decisions: `DECISIONS.md`
- Tracker: `PROJECT_TRACKER.md`
- QA checklist: `docs/QA_CHECKLIST.md`
- V1 scope: `docs/V1_SCOPE.md`
- Build in public: `BLOG_WORKFLOW.md`
