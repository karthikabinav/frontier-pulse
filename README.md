# Frontier Pulse

Frontier Pulse is a local-first research intelligence system for weekly paper ingestion, structured alpha extraction, hypothesis tracking, and human-in-the-loop publication workflows.

## Current Status

This repository is scaffolded for V1 with:
- FastAPI backend (`backend/`)
- PostgreSQL + pgvector via Docker Compose
- React + Vite frontend shell (`frontend/`)
- Modular service boundaries for ingestion, extraction, clustering, and reporting

## Quick Start

### 1. Start Postgres + pgvector

```bash
cd backend
cp .env.example .env
docker compose up -d db
```

### 2. Run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

### 3. Run frontend

```bash
cd frontend
npm install
npm run dev
```

## API docs
- Swagger: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`

## Next Steps
- Complete planner decisions in `PLANNING_QUESTIONS.md`
- Implement real arXiv ingestion
- Wire local LLM provider (Ollama/vLLM)
- Add Alembic migrations and persistence workflow
