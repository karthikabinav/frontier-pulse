# Frontier Pulse Product Action Checklist

Date: 2026-03-01

## Search / Retrieval
- [ ] Implement memory query support with keyword filtering over title/summary/provenance.
- [ ] Add recent-window retrieval (`recent_weeks`) to separate structural trends from stale memory.
- [ ] Add retrieval confidence metadata in response payloads.

## Long-Term Memory (Shifts)
- [ ] Keep weekly synthesis entries as first-class memory artifacts.
- [ ] Add trend continuity checks (same hypothesis persisting over N weeks).
- [ ] Add contradiction drift tracking across weeks.

## Short-Term Memory (Emerging ideas)
- [ ] Tag newly observed mechanisms as `emerging_signal` memory entries.
- [ ] Add "last 7 days" breakout panel in dashboard.
- [ ] Add novelty-first ranking path for early detection.

## Messaging Layer
- [ ] Produce default exports for:
  - research audience
  - product audience
  - VC audience
- [ ] Attach confidence/caveat section in all exports.
- [ ] Keep message templates evidence-grounded, not hype-first.

## QA / Ops
- [ ] Add regression check for memory endpoint filtering.
- [ ] Verify cron output includes audience-ready drafts.
- [ ] Add telemetry: memory growth by type + retrieval usage stats.
