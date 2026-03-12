# Frontier Pulse — Auto-Generated Experiment Plan

Generated: 2026-03-12 01:11 UTC

## 1. H-2026-03-12-ctx-router
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

## 2. H-2026-03-12-reward-shaped-agent
**Claim:** Progress-aware reward shaping increases multi-step task completion for tool-using agents.
**Rationale:** Promise/progress labels should improve sequential credit assignment over sparse terminal reward signals.

### Data
- WebArena-Lite
- AgentTraj Reward Audit Set

### Metrics
- Primary: task_completion_rate
- Secondary: steps_to_success
- Secondary: reward_model_auc
- Secondary: wall_clock_sec

### Trial Matrix
- T0 | baseline | binary terminal reward only | purpose: Reference point
- T1 | intervention | dense reward model with promise/progress labels + GAE smoothing | purpose: Measure gain from proposed change
- T2 | ablation-low-budget | dense reward model with promise/progress labels + GAE smoothing | 50% compute budget | purpose: Test efficiency sensitivity
- T3 | robustness-shift | dense reward model with promise/progress labels + GAE smoothing | distribution shift split | purpose: Check generalization under shift

### Success/Stop Criteria
- Success if `task_completion_rate` improves by >= 3% vs baseline.
- Stop early if no upward trend after 2 completed trials.
- Promote to broader run only if robustness trial does not regress >1%.

### Resource Envelope
- GPU budget: 28 hours
- Max trials: 4
- Estimated wall-clock: 4 days

### Risks & Mitigations
- Confound from data contamination -> enforce split hash checks before run.
- Metric overfitting -> require secondary metric agreement.
- Compute overrun -> cap each trial and checkpoint at 25/50/75% budget.

## 3. H-2026-03-12-latency-routing
**Claim:** Latency-conditioned model routing improves utility per wall-clock under tool latency.
**Rationale:** Smaller models should dominate fast-feedback loops while larger models win in high-latency planning segments.

### Data
- TimelyMachine synthetic suite
- FrontierPulse agent traces 2026-Q1

### Metrics
- Primary: utility_per_minute
- Secondary: success_rate
- Secondary: cost_per_task_usd
- Secondary: latency_p95_ms

### Trial Matrix
- T0 | baseline | single 70B planner for all steps | purpose: Reference point
- T1 | intervention | latency-aware router selecting 8B/70B by budget_remaining_ms | purpose: Measure gain from proposed change
- T2 | ablation-low-budget | latency-aware router selecting 8B/70B by budget_remaining_ms | 50% compute budget | purpose: Test efficiency sensitivity

### Success/Stop Criteria
- Success if `utility_per_minute` improves by >= 3% vs baseline.
- Stop early if no upward trend after 2 completed trials.
- Promote to broader run only if robustness trial does not regress >1%.

### Resource Envelope
- GPU budget: 24 hours
- Max trials: 3
- Estimated wall-clock: 4 days

### Risks & Mitigations
- Confound from data contamination -> enforce split hash checks before run.
- Metric overfitting -> require secondary metric agreement.
- Compute overrun -> cap each trial and checkpoint at 25/50/75% budget.

## 4. H-2026-03-12-citation-robustness
**Claim:** Grounded citation validation reduces hallucinated claims in weekly briefs.
**Rationale:** Claim-evidence verification should lower unsupported statements without major recall loss.

### Data
- Frontier literature digest archive
- ArXiv cs.AI 2025-2026 sample

### Metrics
- Primary: unsupported_claim_rate
- Secondary: brief_recall
- Secondary: editor_time_min
- Secondary: citation_coverage

### Trial Matrix
- T0 | baseline | generation-only weekly summarizer | purpose: Reference point
- T1 | intervention | summarizer + claim-evidence verifier + confidence gating | purpose: Measure gain from proposed change
- T2 | ablation-low-budget | summarizer + claim-evidence verifier + confidence gating | 50% compute budget | purpose: Test efficiency sensitivity
- T3 | robustness-shift | summarizer + claim-evidence verifier + confidence gating | distribution shift split | purpose: Check generalization under shift

### Success/Stop Criteria
- Success if `unsupported_claim_rate` improves by >= 3% vs baseline.
- Stop early if no upward trend after 2 completed trials.
- Promote to broader run only if robustness trial does not regress >1%.

### Resource Envelope
- GPU budget: 18 hours
- Max trials: 4
- Estimated wall-clock: 3 days

### Risks & Mitigations
- Confound from data contamination -> enforce split hash checks before run.
- Metric overfitting -> require secondary metric agreement.
- Compute overrun -> cap each trial and checkpoint at 25/50/75% budget.

---
This plan is machine-generated and ready for review/execution.
