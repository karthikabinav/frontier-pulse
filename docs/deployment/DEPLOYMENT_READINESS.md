# Deployment Readiness (V1 hardening)

Status: **Partially ready** after this pass.

## Completed in this pass
- Added Alembic migration stack (`backend/alembic*` + initial schema migration)
- Switched runtime default to migration-first DB init (`DB_INIT_MODE=migrate`)
- Added CI workflow for backend + frontend build + migration smoke
- Hardened source connectors with retry/backoff + user-agent
- Updated backend runtime docs for migration and scheduler modes

## Remaining before production deployment
1. **Secrets + config management**
   - Configure `OPENROUTER_API_KEY` securely
   - Add production `.env` management (Vault / Doppler / cloud secrets)
2. **Single scheduler instance**
   - Run API with `SCHEDULER_MODE=off` in replicas
   - Run one dedicated worker with `SCHEDULER_MODE=in_process`
3. **Observability**
   - Structured logs (JSON)
   - Error tracking + alerting
4. **Connector expansion**
   - Implement authenticated X connector (current placeholder)
   - Improve full-text ingestion for arXiv PDFs
5. **Benchmark gate**
   - Enforce precision >= 0.70 before publish in CI/nightly QA

## Recommended deployment pattern
- PostgreSQL + pgvector managed instance
- One backend API deployment (FastAPI)
- One scheduler worker deployment (same code, different env)
- Frontend static build served via CDN/edge
