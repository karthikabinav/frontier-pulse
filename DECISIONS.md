# Frontier Pulse Decisions

Last updated: 2026-02-21
Status: Partially finalized

## Confirmed Decisions (from planning answers)

1. Audience and mission
- V1 optimizes for the research community.
- System direction is long-horizon: first step toward an automated AI researcher that identifies durable trends and meaningful hypotheses over time.

2. Schedule
- Ingestion should run automatically every night at **2:00 AM PT**.
- Current default config:
  - `WEEKLY_CRON=0 2 * * *`
  - `WEEKLY_TIMEZONE=America/Los_Angeles`

3. Review target
- 45-minute weekly review is acceptable as target.

4. UX speed
- Prioritize fastest review flow (keyboard-friendly if it improves speed).

5. Versioning + memory
- Drafts must be fully versioned and auditable.
- Background research artifacts must be retained in a neat, indexable long-term memory.

6. Data source scope
- V1 should ingest all relevant sources, not just arXiv:
  - arXiv
  - OpenReview
  - Frontier lab blogs
  - X threads
  - Reddit discussions
  - Major university AI blogs (Stanford, MIT, Berkeley and peers)

7. arXiv category scope
- Initial categories:
  - `cs.CL`, `cs.LG`, `stat.ML`, `cs.AI`, `cs.DS`, `cs.GT`, `cs.MA`

8. Revision policy
- Include revised older papers in ingestion; revisions are considered high-value signal updates.

9. Batch policy
- No hard cap on papers per batch for the focused topic area.

10. Duplicate policy
- Deduplicate using fuzzy title + abstract matching (not arXiv ID only).

11. Build-in-public / personal branding objective
- The project should produce a public narrative while building.
- Weekly progress should be documented as technical build logs.
- Longform writing should be supported by internal docs and export artifacts.

12. PDF parser strategy
- Use primary/fallback parser chain with engineering judgment.
- Default implementation policy:
  - primary: `pymupdf`
  - fallback: `pdfminer`

13. Appendix/reference policy
- Focus on main paper and core claims by default.
- Use appendix/references only when needed for claim interpretation.

14. Equation handling policy
- V1 uses plain text equation extraction.
- Future upgrade path: equation screenshots + multimodal reasoning support.

15. Chunking defaults
- User delegated chunk sizing choice to implementation.
- Default policy selected:
  - target chunk size: 1200 tokens
  - overlap: 150 tokens

16. Section interpretation policy
- Enable semantic section recognition even with noisy headings.
- Extraction should interpret structure in the lens of hypotheses, claims, and results.

17. LLM runtime strategy (inferred from Q16-Q21 + research)
- V1 uses local-first inference with optional cloud fallback.
- Primary runtime: `Ollama` (local).
- Fallback runtime: `OpenRouter` (cloud) when local calls fail or quality/routing requires it.
- Keep model selection configurable to avoid lock-in.

18. Model strategy for V1
- Use one model for extraction + synthesis in V1, with separate config keys for future split.
- Default local model: `qwen2.5:7b-instruct`.
- Default fallback cloud model: `meta-llama/llama-3.1-8b-instruct:free` (can be swapped).

19. Quality vs determinism
- Determinism is not required.
- Default temperature set to `0.35` for higher-quality generation diversity while retaining structure.

20. Cost/runtime guardrails
- Cloud fallback is enabled but budget-capped.
- Initial guardrails:
  - weekly fallback budget: `$5.00`
  - weekly LLM call cap: `600`

## Implemented from these decisions

- Scheduler defaults updated to nightly 2:00 AM PT in:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/.env.example`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/config.py`
- Ingestion defaults updated for multi-source + revision-aware operation in:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/.env.example`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/config.py`
- Persistence models added for long-term traceability in:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/db/models.py`
  - `ResearchBrief`
  - `ResearchBriefVersion`
  - `ResearchMemoryEntry`
- Workflow request schema updated to represent multi-source runs and uncapped batches:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/schemas/domain.py`
- Parsing and chunking defaults added to backend runtime settings:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/.env.example`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/config.py`
- Ingestion policy API expanded to expose parsing policy:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/schemas/domain.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/services/stub_impl.py`
- Inference defaults, runtime guardrails, and policy API added:
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/.env.example`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/config.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/schemas/domain.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/api/v1/workflows.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/services/inference.py`
  - `/Users/karthikabinav/kabinav/frontier-pulse/backend/app/services/stub_impl.py`
- Build-in-public workflow and templates added:
  - `/Users/karthikabinav/kabinav/frontier-pulse/BLOG_WORKFLOW.md`
  - `/Users/karthikabinav/kabinav/frontier-pulse/content/blog/templates/weekly_build_log.md`
  - `/Users/karthikabinav/kabinav/frontier-pulse/content/blog/drafts/2026-02-21-kickoff.md`

## Open Decisions (priority)

- Filter scope: initial keyword list for inference-time compute + reasoning optimization.
- Output provenance: required citation/snippets per generated claim.
- Scoring semantics: novelty and strength numeric scales and human override behavior.

## Temporary Defaults Until Answered

- Source: multi-source ingestion enabled.
- Max weekly papers: uncapped (`0` sentinel until full scheduler/worker controls are added).
- Local inference provider: Ollama.
- Embeddings: `nomic-embed-text`.
- No cloud fallback unless explicitly enabled.

These defaults are placeholders and should be finalized before deep Phase 2 implementation.
