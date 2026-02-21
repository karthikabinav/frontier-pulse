# Frontier Pulse Project Tracker

Last updated: 2026-02-21
Project path: `/Users/karthikabinav/kabinav/frontier-pulse`

## 1) Current Snapshot

### Completed
- Created new project folder outside old site repo.
- Added root docs:
  - `README.md`
  - `PLANNING_QUESTIONS.md`
- Scaffolded backend (`FastAPI`, modular boundaries):
  - API routers for health, papers, weekly workflow trigger.
  - Config and environment template.
  - DB layer scaffold with SQLAlchemy models and pgvector field placeholders.
  - Service contracts and stub implementations.
  - Docker Compose for Postgres + pgvector.
- Scaffolded frontend (`React + Vite`):
  - Basic dashboard shell.
  - API health fetch integration.
- Added canonical decision log:
  - `DECISIONS.md`
- Applied confirmed product decisions from planning Q1-Q5:
  - Nightly schedule defaults set to 2:00 AM PT.
  - Data model expanded for draft versioning and long-term research memory indexing.
- Applied confirmed data-scope decisions from planning Q6-Q10:
  - Multi-source ingestion requirement captured in config.
  - arXiv category expansion captured in config.
  - Revised-paper inclusion enabled by default.
  - Uncapped batch policy represented by `max_papers=0` sentinel.
  - Fuzzy title+abstract dedupe strategy documented as default.
- Applied confirmed parsing/preprocessing decisions from planning Q11-Q15:
  - Parser chain defaults set (`pymupdf` primary, `pdfminer` fallback).
  - Main-paper-first appendix policy captured.
  - Equation handling set to plain-text V1.
  - Chunking defaults set (1200 target / 150 overlap).
  - Semantic sectioning enabled for noisy headings.
- Added ingestion policy API contract for cross-agent/UI consistency:
  - `GET /api/v1/workflows/ingestion-policy`
- Added inference policy API contract for cross-agent/UI consistency:
  - `GET /api/v1/workflows/inference-policy`
- Added local-first inference adapter scaffold with optional cloud failover:
  - `backend/app/services/inference.py`
- Added build-in-public documentation system:
  - `BLOG_WORKFLOW.md`
  - Weekly blog template
  - Week 1 kickoff draft

### Tested / Verified
- File scaffolding and directory layout verified.
- Verified decision and tracker docs exist and are updated.
- Endpoints and frontend were **not runtime-tested yet** (no install/run executed yet).
- No unit/integration tests exist yet.

### Pending (High Level)
- Finalize remaining product decisions from planning questionnaire (Q22+).
- Implement real ingestion pipeline (arXiv API + PDF download + parse + chunk).
- Implement additional source connectors (OpenReview/blogs/X/Reddit/university blogs).
- Implement local LLM extraction pipeline with strict JSON schema outputs.
- Implement embeddings + pgvector indexing + retrieval endpoints.
- Implement hypothesis builder, clustering, tension detection.
- Implement weekly report builder and export generation.
- Implement review UX actions and persistence.
- Add tests, observability, and runbooks.
- Build blog/export integration so weekly progress can be published for personal branding.

## 2) Master Plan (Execution Phases)

### Phase 0: Decision Freeze (Required)
Goal: lock defaults so implementation does not thrash.
- Confirm provider stack (Ollama vs vLLM).
- Confirm model choices (extraction + synthesis if split).
- Confirm ingestion window and filters.
- Confirm schema decisions (mutable vs immutable cards, scoring scales, provenance).
- Confirm UX priorities for V1 vs V1.1.

Exit criteria:
- Planning answers captured in one canonical config document.

### Phase 1: Core Data + Ingestion
Goal: reliably ingest weekly papers into DB.
- Set up DB migrations (Alembic).
- Implement arXiv client with category + keyword filters.
- Implement dedupe (arXiv ID + optional fuzzy title).
- Implement PDF fetch + parser fallback chain.
- Implement section extraction + chunking.
- Persist papers, chunks, metadata.

Exit criteria:
- One command ingests a weekly batch and stores papers/chunks.

### Phase 2: Extraction + Hypothesis Engine
Goal: structured alpha artifacts from local models.
- Add pluggable inference adapter interface.
- Implement Ollama adapter (vLLM adapter stub optional).
- Add prompt templates with strict JSON schema + retries.
- Generate and store `PaperAlphaCard` records.
- Build hypothesis extraction pass across alpha cards.
- Build contradiction/support links and confidence scoring.

Exit criteria:
- Weekly run yields alpha cards and hypothesis graph records.

### Phase 3: Embeddings + Clustering + Tensions
Goal: semantic grouping and frontier map.
- Add embedding adapter and persistence.
- Build vector retrieval utilities + metadata filtering.
- Add clustering job (HDBSCAN or agglomerative fallback).
- Add tension detector (contradiction-focused edges).
- Generate graph export JSON + PNG render.

Exit criteria:
- Clusters and tensions visible from API and stored in DB.

### Phase 4: Human-in-the-Loop UI
Goal: 45-minute review workflow.
- Build cluster review panel (rename, merge/split if in scope).
- Build hypothesis table with user ratings/comments.
- Build tension panel (accept/reject/nuance).
- Build alpha notes editor and weekly draft artifact.
- Build “Generate Public Versions” gated by user approval.

Exit criteria:
- End-to-end weekly review and publish-ready drafts.

### Phase 5: Export + QA + Hardening
Goal: consistent publication quality.
- Add Twitter/X thread formatter.
- Add LinkedIn formatter.
- Add markdown longform exporter.
- Add regression tests + golden prompt cases.
- Add operational docs and troubleshooting guide.

Exit criteria:
- 2-3 consecutive weekly runs completed without manual code fixes.

## 3) Task Board (Parallel Workstreams)

## WS-A Backend Platform
Owner: Agent A
Status: In progress (scaffold done)
Tasks:
- Add Alembic migration stack.
- Replace stub services with real repositories and transactions.
- Add typed service errors and API error contracts.
- Add scheduler wiring (APScheduler or separate worker).
- Add persistence CRUD for `ResearchBrief`, `ResearchBriefVersion`, `ResearchMemoryEntry`.
Dependencies: planning freeze for scheduler mode.

## WS-B Ingestion and Parsing
Owner: Agent B
Status: Pending
Tasks:
- arXiv query module.
- Multi-source connector interfaces and source-specific fetchers.
- PDF downloader with retry/backoff.
- Parser pipeline (`pymupdf` primary, fallback parser).
- Section/chunk extraction and cleaning rules.
Dependencies: decisions on runtime/model stack (Q16+).

## WS-C LLM Inference and Prompts
Owner: Agent C
Status: In progress (policy + adapter scaffold done)
Tasks:
- Prompt templates for `PaperAlphaCard`.
- JSON schema validation and retry strategy.
- Batch orchestration and timeout strategy.
- Budget tracking and fallback call accounting.
Dependencies: embedding and schema decisions.

## WS-D Hypothesis + Clustering
Owner: Agent D
Status: Pending
Tasks:
- Hypothesis synthesis from alpha cards.
- Support/contradiction edge generation.
- Clustering module and label synthesis.
- Graph export (JSON + image).
Dependencies: alpha card persistence and embeddings.

## WS-E Frontend Review UX
Owner: Agent E
Status: In progress (shell done)
Tasks:
- Data fetch layer and query state.
- Cluster panel + hypothesis table + tension panel.
- Alpha notes editor.
- Draft version history UI and compare view.
- Export action flow with approval gating.
Dependencies: backend endpoints.

## WS-F Testing and QA
Owner: Agent F
Status: Pending
Tasks:
- Unit tests for parser, prompt validators, scoring.
- Integration tests for weekly workflow.
- Fixtures/golden set for regression.
- Smoke test script for local setup.
Dependencies: core modules completed.

## WS-G Build In Public
Owner: Agent G
Status: In progress (workflow docs + first draft done)
Tasks:
- Keep weekly build log drafts updated from tracker/decisions.
- Add backend endpoint(s) to compile weekly blog-ready changelog payload.
- Add UI action to generate blog draft from current weekly artifacts.
- Add platform-specific derivative formatters (LinkedIn/X summary from canonical longform draft).
Dependencies: tracker updates, export pipeline.

## 4) Immediate Next Actions (Recommended Order)

1. Answer planning questions in `PLANNING_QUESTIONS.md`.
2. Continue updating `DECISIONS.md` as answers arrive (single source of truth).
3. Implement Phase 1 ingestion with DB migrations.
4. Implement persistence APIs for brief versioning + research memory.
5. Implement Phase 2 extraction on top of ingested chunks.
6. Add minimal end-to-end integration test for weekly run.
7. Start weekly publish loop using `BLOG_WORKFLOW.md` and the template draft.

## 5) Resume Checklist for Any Agent

Before coding:
- Confirm working directory is `/Users/karthikabinav/kabinav/frontier-pulse`.
- Read these docs in order:
  1. `PROJECT_TRACKER.md`
  2. `PLANNING_QUESTIONS.md`
  3. `README.md`
- Check unresolved decisions first; avoid speculative implementation.

Before handoff:
- Update this file sections:
  - Completed
  - Tested / Verified
  - Pending
  - Workstream status
- Add exact commands used for validation.
- List risks or blockers for next agent.

## 6) Known Risks / Blockers Right Now

- Product decisions are partially frozen; unresolved Q11+ can still cause rework.
- Runtime environment (Python/Node versions, Docker availability) unverified.
- Local model runtime path (Ollama vs vLLM) not locked.
- Inference runtime defaults are set, but need runtime validation on target machine.
- No DB migrations or seed data flow yet.

## 7) Validation Log

No runtime validation executed yet.
- Not run: backend install
- Not run: frontend install
- Not run: docker compose
- Not run: API smoke test

(Only filesystem scaffold verification completed.)
