# Frontier Pulse Backend

## Run

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## API

- `GET /api/v1/health`
- `GET /api/v1/papers`
- `POST /api/v1/workflows/weekly-run`
- `GET /api/v1/workflows/ingestion-policy`
- `GET /api/v1/workflows/inference-policy`
- `GET /api/v1/workflows/project-policy`
