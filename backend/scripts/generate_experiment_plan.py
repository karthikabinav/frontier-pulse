#!/usr/bin/env python3
"""Generate a concrete experiment plan from structured hypothesis inputs.

This artifact is meant to support autonomous AI research workflows by turning
hypothesis specs into reproducible, reviewer-friendly plans.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class HypothesisSpec:
    hypothesis_id: str
    claim: str
    rationale: str
    baseline: str
    intervention: str
    datasets: list[str]
    primary_metric: str
    secondary_metrics: list[str]
    budget_gpu_hours: int
    max_trials: int



def _load_specs(path: Path) -> list[HypothesisSpec]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("Input JSON must be a list of hypothesis specs")

    specs: list[HypothesisSpec] = []
    for item in payload:
        specs.append(
            HypothesisSpec(
                hypothesis_id=str(item["hypothesis_id"]),
                claim=str(item["claim"]),
                rationale=str(item["rationale"]),
                baseline=str(item["baseline"]),
                intervention=str(item["intervention"]),
                datasets=[str(x) for x in item.get("datasets", [])],
                primary_metric=str(item["primary_metric"]),
                secondary_metrics=[str(x) for x in item.get("secondary_metrics", [])],
                budget_gpu_hours=int(item.get("budget_gpu_hours", 16)),
                max_trials=int(item.get("max_trials", 4)),
            )
        )
    return specs



def _build_trial_matrix(spec: HypothesisSpec) -> list[dict[str, Any]]:
    # Simple but useful matrix: baseline, intervention, and two stress tests.
    return [
        {
            "trial": "T0",
            "condition": "baseline",
            "config": spec.baseline,
            "purpose": "Reference point",
        },
        {
            "trial": "T1",
            "condition": "intervention",
            "config": spec.intervention,
            "purpose": "Measure gain from proposed change",
        },
        {
            "trial": "T2",
            "condition": "ablation-low-budget",
            "config": f"{spec.intervention} | 50% compute budget",
            "purpose": "Test efficiency sensitivity",
        },
        {
            "trial": "T3",
            "condition": "robustness-shift",
            "config": f"{spec.intervention} | distribution shift split",
            "purpose": "Check generalization under shift",
        },
    ][: max(2, min(spec.max_trials, 4))]



def _estimate_timeline_days(spec: HypothesisSpec) -> int:
    # Coarse scheduler for autonomous planning.
    prep = 1
    execution = max(1, spec.budget_gpu_hours // 12)
    analysis = 1
    return prep + execution + analysis



def _render_markdown(specs: list[HypothesisSpec]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        "# Frontier Pulse — Auto-Generated Experiment Plan",
        "",
        f"Generated: {stamp}",
        "",
    ]

    for idx, spec in enumerate(specs, start=1):
        matrix = _build_trial_matrix(spec)
        timeline_days = _estimate_timeline_days(spec)

        data_lines = [f"- {d}" for d in spec.datasets] if spec.datasets else ["- (none specified)"]
        metric_lines = [f"- Secondary: {m}" for m in spec.secondary_metrics]

        lines.extend(
            [
                f"## {idx}. {spec.hypothesis_id}",
                f"**Claim:** {spec.claim}",
                f"**Rationale:** {spec.rationale}",
                "",
                "### Data",
                *data_lines,
                "",
                "### Metrics",
                f"- Primary: {spec.primary_metric}",
                *metric_lines,
                "",
                "### Trial Matrix",
            ]
        )

        for row in matrix:
            lines.append(
                f"- {row['trial']} | {row['condition']} | {row['config']} | purpose: {row['purpose']}"
            )

        lines.extend(
            [
                "",
                "### Success/Stop Criteria",
                f"- Success if `{spec.primary_metric}` improves by >= 3% vs baseline.",
                "- Stop early if no upward trend after 2 completed trials.",
                "- Promote to broader run only if robustness trial does not regress >1%.",
                "",
                "### Resource Envelope",
                f"- GPU budget: {spec.budget_gpu_hours} hours",
                f"- Max trials: {spec.max_trials}",
                f"- Estimated wall-clock: {timeline_days} days",
                "",
                "### Risks & Mitigations",
                "- Confound from data contamination -> enforce split hash checks before run.",
                "- Metric overfitting -> require secondary metric agreement.",
                "- Compute overrun -> cap each trial and checkpoint at 25/50/75% budget.",
                "",
            ]
        )

    lines.append("---")
    lines.append("This plan is machine-generated and ready for review/execution.")
    return "\n".join(lines) + "\n"



def _render_json(specs: list[HypothesisSpec]) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(specs),
        "plans": [
            {
                "hypothesis_id": s.hypothesis_id,
                "claim": s.claim,
                "primary_metric": s.primary_metric,
                "secondary_metrics": s.secondary_metrics,
                "timeline_days": _estimate_timeline_days(s),
                "trial_matrix": _build_trial_matrix(s),
            }
            for s in specs
        ],
    }



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment plans from hypothesis specs")
    parser.add_argument("--input", required=True, help="Path to input JSON list of hypotheses")
    parser.add_argument("--output-md", required=True, help="Output markdown plan path")
    parser.add_argument("--output-json", help="Optional output JSON path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json) if args.output_json else None

    specs = _load_specs(input_path)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_render_markdown(specs))

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(_render_json(specs), indent=2))

    print(f"Generated plan for {len(specs)} hypotheses -> {output_md}")
    if output_json:
        print(f"Structured artifact -> {output_json}")


if __name__ == "__main__":
    main()
