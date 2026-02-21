# Frontier Pulse Decisions

Last updated: 2026-02-21
Status: Finalized for V1

## Mission and Product
1. Audience is the research community.
2. Mission is to build the first step of an open automated AI researcher.
3. Weekly review target is 45 minutes (acceptable target).
4. UX should prioritize speed (hotkeys enabled).
5. Drafts and memory must be versioned and auditable.

## Scheduling
6. Ingestion runs nightly at 2:00 AM PT.
7. Timezone is `America/Los_Angeles`.
8. First real weekly run target is Monday morning, 2026-02-23.

## Sources and Retrieval
9. Multi-source ingestion in V1: arXiv, OpenReview, frontier lab blogs, X threads, Reddit, major university AI blogs.
10. arXiv categories: `cs.CL`, `cs.LG`, `stat.ML`, `cs.AI`, `cs.DS`, `cs.GT`, `cs.MA`.
11. Revised older papers are included.
12. No hard paper cap per batch in focused scope.
13. Deduplication uses fuzzy title + abstract matching.

## Parsing and Preprocessing
14. Parser chain: `pymupdf` primary, `pdfminer` fallback.
15. Main-paper-first policy; use appendices/references only when needed.
16. Equation policy is plain text for V1; multimodal equation handling deferred.
17. Chunk defaults: 1200 target tokens, 150 overlap.
18. Semantic section interpretation enabled, even with noisy headings.

## LLM Inference
19. Local-first inference runtime.
20. Primary provider: Ollama.
21. Optional cloud fallback: OpenRouter with budget guardrails.
22. Single model for extraction + synthesis in V1, configurable split later.
23. Default local model: `qwen2.5:7b-instruct`.
24. Default cloud fallback model: `meta-llama/llama-3.1-8b-instruct:free`.
25. Temperature is quality-oriented, not deterministic (`0.35`).
26. Weekly fallback budget cap: `$5.00`; weekly call cap: `600`.

## Embeddings and Retrieval (inferred defaults)
27. Embedding model: `nomic-embed-text`.
28. Embedding scope: both section chunks and full paper.
29. Vector search with metadata filters is enabled in V1.

## Schema and Evidence
30. Alpha cards are immutable snapshots with history.
31. Novelty score mode: ordinal buckets.
32. Hypothesis strength: model default with human override.
33. Contradictions are explicit edges with confidence.
34. Provenance/citations per claim are required.

## Human-in-the-Loop UX
35. Auth is skipped for local V1.
36. Cluster merge/split is deferred to V1.1.
37. Hypothesis user rating scale: binary.
38. Inline citations/snippets required beside generated claims.
39. Editor mode: markdown for V1.
40. Hotkeys are required for fast review.

## Exports
41. Twitter/X export mode: classic thread.
42. LinkedIn tone: founder voice.
43. V1 export defaults to text-only (no visuals by default).
44. Template mode is shared in V1; optional platform divergence later.
45. Export delivery mode: one-click clipboard.

## Infrastructure and Ops (inferred defaults)
46. V1 deployment mode: local only; GitHub code push expected.
47. DB backend: Postgres.
48. Development runtime: native-first.
49. Scheduler mode: in-process scheduler for V1 simplicity.
50. Backups required: retain last 7 days of DB snapshots.

## Quality and Rollout
51. Minimum acceptable extraction precision before rollout: >= 0.70.
52. Manual QA checklist is enabled before export.
53. Model drift tracking is disabled in V1.
54. Benchmark set (10-20 papers) is required for regression.
55. Primary metric priority: output quality > insight novelty.
56. Rollout plan: start on separate X/LinkedIn accounts; blog the build process in parallel.

## Security and Privacy
57. Only public data expected in V1.
58. Exported outputs must redact absolute local filesystem paths.
59. DB at-rest encryption deferred for V1.

## V1 Scope Priorities
60. Non-negotiables:
- Frontier-source paper scouring + filtration for relevant insight.
- Structured traceable extraction with citations.
- Long-horizon memory/versioning foundation for future AI researcher behavior.
61. Deferred to V1.1:
- Full cluster merge/split UX.
- Visual asset export pipeline.
- Multi-user auth + hosted deployment.
62. Execution priority: backend correctness over review UX speed.

## Implemented Artifacts
- Runtime defaults: `/Users/karthikabinav/kabinav/frontier-pulse/backend/.env.example`
- Settings model: `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/config.py`
- Ingestion/inference policy APIs:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/api/v1/workflows.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/schemas/domain.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/services/stub_impl.py`
- Build-in-public workflow:
  - `/Users/karthikabinav/kabinav/frontier-pulse/BLOG_WORKFLOW.md`
  - `/Users/karthikabinav/kabinav/frontier-pulse/content/blog/templates/weekly_build_log.md`
