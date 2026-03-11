# Frontier Pulse — Auto-Generated Experiment Plan

Generated: 2026-03-11 17:29 UTC

## 1. H-2026-03-11-ctx-router
**Claim:** Adaptive context routing to specialist tool-using heads improves pass@1 on long-horizon research QA.
**Rationale:** Routing should reduce irrelevant token usage and increase retrieval precision under fixed context windows.

### Data
- LongForm Research QA v2
- FrontierPulse internal benchmark set A

### Metrics
- Primary: pass@1
- Secondary: token_cost_per_answer
- Secondary: citation_precision
- Secondary: latency_p95_ms

### Trial Matrix
- T0 | baseline | single-policy-agent + fixed retrieval top_k=12 | purpose: Reference point
- T1 | intervention | mixture-of-experts router + per-head retrieval top_k in {4,8,12} | purpose: Measure gain from proposed change
- T2 | ablation-low-budget | mixture-of-experts router + per-head retrieval top_k in {4,8,12} | 50% compute budget | purpose: Test efficiency sensitivity
- T3 | robustness-shift | mixture-of-experts router + per-head retrieval top_k in {4,8,12} | distribution shift split | purpose: Check generalization under shift

### Success/Stop Criteria
- Success if `pass@1` improves by >= 3% vs baseline.
- Stop early if no upward trend after 2 completed trials.
- Promote to broader run only if robustness trial does not regress >1%.

### Resource Envelope
- GPU budget: 36 hours
- Max trials: 4
- Estimated wall-clock: 5 days

### Risks & Mitigations
- Confound from data contamination -> enforce split hash checks before run.
- Metric overfitting -> require secondary metric agreement.
- Compute overrun -> cap each trial and checkpoint at 25/50/75% budget.

---
This plan is machine-generated and ready for review/execution.
