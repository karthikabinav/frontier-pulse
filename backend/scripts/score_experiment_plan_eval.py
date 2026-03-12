#!/usr/bin/env python3
"""Executable eval slice for experiment-plan generation.

Compares a weak baseline planner vs current planner logic on a fixture of
research hypotheses (including at least one edge/failure case).
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any

try:
    from scripts.generate_experiment_plan import (
        HypothesisSpec,
        _build_trial_matrix,
        _estimate_timeline_days,
    )
except ModuleNotFoundError:
    from generate_experiment_plan import (  # type: ignore
        HypothesisSpec,
        _build_trial_matrix,
        _estimate_timeline_days,
    )


def _load_fixture(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("Fixture must be a JSON list")
    return payload


def _spec_from_item(item: dict[str, Any]) -> HypothesisSpec:
    return HypothesisSpec(
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


def _baseline_plan(spec: HypothesisSpec) -> dict[str, Any]:
    return {
        "hypothesis_id": spec.hypothesis_id,
        "primary_metric": spec.primary_metric,
        "secondary_metrics": [],
        "timeline_days": 2,
        "trial_matrix": [
            {"trial": "T0", "condition": "baseline"},
            {"trial": "T1", "condition": "intervention"},
        ],
    }


def _current_plan(spec: HypothesisSpec) -> dict[str, Any]:
    return {
        "hypothesis_id": spec.hypothesis_id,
        "primary_metric": spec.primary_metric,
        "secondary_metrics": spec.secondary_metrics,
        "timeline_days": _estimate_timeline_days(spec),
        "trial_matrix": _build_trial_matrix(spec),
    }


def _quality_score(plan: dict[str, Any], spec: HypothesisSpec) -> float:
    trials = plan.get("trial_matrix", [])
    conditions = {row.get("condition") for row in trials if isinstance(row, dict)}

    checks = [
        1.0 if len(trials) >= 3 else 0.0,
        1.0 if "robustness-shift" in conditions else 0.0,
        1.0 if plan.get("timeline_days", 0) >= 3 else 0.0,
        min(1.0, len(plan.get("secondary_metrics", [])) / max(1, len(spec.secondary_metrics))),
    ]
    return sum(checks) / len(checks)


def _evaluate_model(
    model_name: str,
    rows: list[dict[str, Any]],
    planner,
) -> dict[str, Any]:
    successes = 0
    expected_failures = 0
    expected_failures_caught = 0
    quality_scores: list[float] = []
    plans: list[dict[str, Any]] = []

    for row in rows:
        expect_failure = bool(row.get("expected_failure", False))
        try:
            spec = _spec_from_item(row)
            plan = planner(spec)
            plans.append(plan)
            if expect_failure:
                # Unexpectedly passed malformed fixture.
                continue
            successes += 1
            quality_scores.append(_quality_score(plan, spec))
        except Exception as exc:  # noqa: BLE001
            if expect_failure:
                expected_failures += 1
                expected_failures_caught += 1
                plans.append(
                    {
                        "hypothesis_id": row.get("hypothesis_id", "unknown"),
                        "expected_failure": True,
                        "error": str(exc),
                    }
                )
            else:
                plans.append(
                    {
                        "hypothesis_id": row.get("hypothesis_id", "unknown"),
                        "expected_failure": False,
                        "error": str(exc),
                    }
                )

    valid_cases = sum(1 for r in rows if not bool(r.get("expected_failure", False)))
    fail_cases = sum(1 for r in rows if bool(r.get("expected_failure", False)))
    success_rate = successes / max(1, valid_cases)
    fail_handle_rate = expected_failures_caught / max(1, fail_cases)
    avg_quality = mean(quality_scores) if quality_scores else 0.0
    overall = 0.6 * avg_quality + 0.3 * success_rate + 0.1 * fail_handle_rate

    return {
        "model": model_name,
        "valid_cases": valid_cases,
        "expected_failure_cases": fail_cases,
        "successes": successes,
        "expected_failures_caught": expected_failures_caught,
        "success_rate": round(success_rate, 4),
        "failure_handling_rate": round(fail_handle_rate, 4),
        "avg_quality_score": round(avg_quality, 4),
        "overall_score": round(overall, 4),
        "plans": plans,
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Frontier Pulse Eval Slice Results",
        "",
        f"Fixture: `{summary['fixture_path']}`",
        f"Runs: {summary['runs']}",
        "",
        "## Aggregate Metrics (Baseline vs Current)",
        "",
        "| model | success_rate | failure_handling_rate | avg_quality_score | overall_score |",
        "|---|---:|---:|---:|---:|",
        f"| baseline | {summary['aggregate']['baseline']['success_rate_mean']:.3f} | {summary['aggregate']['baseline']['failure_handling_rate_mean']:.3f} | {summary['aggregate']['baseline']['avg_quality_score_mean']:.3f} | {summary['aggregate']['baseline']['overall_score_mean']:.3f} |",
        f"| current | {summary['aggregate']['current']['success_rate_mean']:.3f} | {summary['aggregate']['current']['failure_handling_rate_mean']:.3f} | {summary['aggregate']['current']['avg_quality_score_mean']:.3f} | {summary['aggregate']['current']['overall_score_mean']:.3f} |",
        "",
        "## Per-run Metrics",
        "",
    ]

    for run in summary["runs_detail"]:
        lines.extend(
            [
                f"### Run {run['run_id']} (seed={run['seed']})",
                f"- baseline overall_score: {run['baseline']['overall_score']:.3f}",
                f"- current overall_score: {run['current']['overall_score']:.3f}",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Score baseline vs current experiment-plan generation")
    parser.add_argument(
        "--fixture",
        default="artifacts/evals/hypothesis_eval_fixture.json",
        help="Path to benchmark fixture JSON",
    )
    parser.add_argument("--runs", type=int, default=3, help="Number of evaluation runs")
    parser.add_argument(
        "--output-json",
        default="artifacts/evals/results_latest.json",
        help="Path to write structured eval results",
    )
    parser.add_argument(
        "--output-md",
        default="artifacts/evals/results_latest.md",
        help="Path to write human-readable summary",
    )
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    rows = _load_fixture(fixture_path)

    runs_detail = []
    for run_id in range(1, args.runs + 1):
        seed = 100 + run_id
        rng = random.Random(seed)
        shuffled = rows[:]
        rng.shuffle(shuffled)

        baseline = _evaluate_model("baseline", shuffled, _baseline_plan)
        current = _evaluate_model("current", shuffled, _current_plan)

        runs_detail.append(
            {
                "run_id": run_id,
                "seed": seed,
                "baseline": baseline,
                "current": current,
            }
        )

    def agg(metric: str, model: str) -> float:
        vals = [r[model][metric] for r in runs_detail]
        return mean(vals)

    summary = {
        "fixture_path": str(fixture_path),
        "runs": args.runs,
        "runs_detail": runs_detail,
        "aggregate": {
            "baseline": {
                "success_rate_mean": agg("success_rate", "baseline"),
                "failure_handling_rate_mean": agg("failure_handling_rate", "baseline"),
                "avg_quality_score_mean": agg("avg_quality_score", "baseline"),
                "overall_score_mean": agg("overall_score", "baseline"),
            },
            "current": {
                "success_rate_mean": agg("success_rate", "current"),
                "failure_handling_rate_mean": agg("failure_handling_rate", "current"),
                "avg_quality_score_mean": agg("avg_quality_score", "current"),
                "overall_score_mean": agg("overall_score", "current"),
            },
        },
    }

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2))
    output_md.write_text(_render_markdown(summary))

    print(json.dumps({"output_json": str(output_json), "output_md": str(output_md)}, indent=2))


if __name__ == "__main__":
    main()
