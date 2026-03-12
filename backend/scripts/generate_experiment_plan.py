#!/usr/bin/env python3
"""Generate a concrete experiment plan from structured hypothesis inputs.

This artifact supports autonomous AI research workflows by turning
hypothesis specs into reproducible, reviewer-friendly plans.

GO-ready hardening:
- strict schema validation
- structured and human-readable failure analysis artifacts
- robust error handling with actionable mitigation notes
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator


class HypothesisSpec(BaseModel):
    hypothesis_id: str = Field(min_length=3, max_length=128)
    claim: str = Field(min_length=10, max_length=2000)
    rationale: str = Field(min_length=10, max_length=2000)
    baseline: str = Field(min_length=3, max_length=500)
    intervention: str = Field(min_length=3, max_length=500)
    datasets: list[str] = Field(default_factory=list, max_length=20)
    primary_metric: str = Field(min_length=2, max_length=120)
    secondary_metrics: list[str] = Field(default_factory=list, max_length=20)
    budget_gpu_hours: int = Field(default=16, ge=1, le=5000)
    max_trials: int = Field(default=4, ge=2, le=4)

    @field_validator("datasets", "secondary_metrics", mode="after")
    @classmethod
    def _non_empty_items(cls, items: list[str]) -> list[str]:
        clean = [x.strip() for x in items if str(x).strip()]
        if len(clean) != len(items):
            raise ValueError("array contains empty/blank strings")
        return clean


class PlanGenerationError(Exception):
    """Raised when generation fails with a user-actionable message."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _load_specs(path: Path) -> list[HypothesisSpec]:
    if not path.exists():
        raise PlanGenerationError(f"Input file not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlanGenerationError(
            f"Invalid JSON in {path}: line {exc.lineno}, col {exc.colno}, {exc.msg}"
        ) from exc
    except OSError as exc:
        raise PlanGenerationError(f"Unable to read input file {path}: {exc}") from exc

    if not isinstance(payload, list):
        raise PlanGenerationError("Input JSON must be a list of hypothesis specs")
    if not payload:
        raise PlanGenerationError("Input JSON list is empty; provide at least one hypothesis spec")

    specs: list[HypothesisSpec] = []
    validation_errors: list[dict[str, Any]] = []

    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            validation_errors.append(
                {
                    "index": idx,
                    "error": "Each hypothesis spec must be a JSON object",
                    "received_type": type(item).__name__,
                }
            )
            continue

        try:
            specs.append(HypothesisSpec.model_validate(item))
        except ValidationError as exc:
            validation_errors.append(
                {
                    "index": idx,
                    "hypothesis_id": item.get("hypothesis_id"),
                    "errors": exc.errors(),
                }
            )

    if validation_errors:
        raise PlanGenerationError(
            "Schema validation failed for one or more hypothesis specs: "
            f"{json.dumps(validation_errors, ensure_ascii=False, default=str)}"
        )

    return specs


def _build_trial_matrix(spec: HypothesisSpec) -> list[dict[str, Any]]:
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
    ][: spec.max_trials]


def _estimate_timeline_days(spec: HypothesisSpec) -> int:
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
        "generated_at_utc": _utc_now(),
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


def _render_failure_analysis_markdown(
    *, input_path: Path, error_message: str, traceback_text: str | None = None
) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Frontier Pulse — Experiment Plan Failure Analysis",
        "",
        f"Generated: {stamp}",
        f"Input: `{input_path}`",
        "",
        "## Failure Summary",
        f"- Status: failed",
        f"- Error: {error_message}",
        "",
        "## Likely Causes",
        "- Input JSON malformed or not UTF-8 encoded.",
        "- Spec schema mismatch (missing required fields, wrong types, or out-of-range values).",
        "- File I/O issue (missing path or permission denied).",
        "",
        "## Mitigation Notes",
        "1. Validate JSON shape before run: top-level list of objects.",
        "2. Ensure each item includes required keys: hypothesis_id, claim, rationale, baseline, intervention, primary_metric.",
        "3. Keep constraints in range: budget_gpu_hours >= 1, max_trials in [2,4], no blank dataset/metric values.",
        "4. Re-run generator after fixing input and verify both markdown + json outputs exist.",
    ]

    if traceback_text:
        lines.extend(["", "## Exception Trace", "```", traceback_text.strip(), "```"])

    lines.append("")
    return "\n".join(lines)


def _render_failure_analysis_json(*, input_path: Path, error_message: str) -> dict[str, Any]:
    return {
        "generated_at_utc": _utc_now(),
        "status": "failed",
        "input": str(input_path),
        "error": error_message,
        "mitigations": [
            "Validate JSON and schema before execution",
            "Ensure required fields and type constraints are satisfied",
            "Confirm file paths/permissions",
            "Retry generation and verify both outputs",
        ],
    }


def _default_failure_md_path(output_md: Path) -> Path:
    return output_md.with_name(f"{output_md.stem}_failure_analysis.md")


def _default_failure_json_path(output_md: Path) -> Path:
    return output_md.with_name(f"{output_md.stem}_failure_analysis.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate experiment plans from hypothesis specs")
    parser.add_argument("--input", required=True, help="Path to input JSON list of hypotheses")
    parser.add_argument("--output-md", required=True, help="Output markdown plan path")
    parser.add_argument("--output-json", help="Optional output JSON path")
    parser.add_argument(
        "--failure-analysis-md",
        help="Optional path for failure analysis markdown (written on error)",
    )
    parser.add_argument(
        "--failure-analysis-json",
        help="Optional path for failure analysis JSON (written on error)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json) if args.output_json else None
    failure_md = Path(args.failure_analysis_md) if args.failure_analysis_md else _default_failure_md_path(output_md)
    failure_json = (
        Path(args.failure_analysis_json)
        if args.failure_analysis_json
        else _default_failure_json_path(output_md)
    )

    try:
        specs = _load_specs(input_path)
        _safe_write_text(output_md, _render_markdown(specs))

        if output_json:
            _safe_write_text(output_json, json.dumps(_render_json(specs), indent=2))

        print(f"Generated plan for {len(specs)} hypotheses -> {output_md}")
        if output_json:
            print(f"Structured artifact -> {output_json}")
        return 0
    except Exception as exc:  # noqa: BLE001 - intentional top-level hardening.
        message = str(exc)
        failure_md_content = _render_failure_analysis_markdown(
            input_path=input_path,
            error_message=message,
        )
        failure_json_content = _render_failure_analysis_json(
            input_path=input_path,
            error_message=message,
        )

        try:
            _safe_write_text(failure_md, failure_md_content)
            _safe_write_text(failure_json, json.dumps(failure_json_content, indent=2))
            print(f"Failure analysis written -> {failure_md}")
            print(f"Failure analysis (json) -> {failure_json}")
        except Exception as write_exc:  # noqa: BLE001
            print(f"ERROR: Failed to write failure artifacts: {write_exc}", file=sys.stderr)

        print(f"ERROR: Experiment plan generation failed: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
