# Frontier Pulse — Experiment Plan Failure Analysis

Generated: 2026-03-12 01:11 UTC
Input: `artifacts/plans/invalid_hypotheses.json`

## Failure Summary
- Status: failed
- Error: Schema validation failed for one or more hypothesis specs: [{"index": 0, "hypothesis_id": "H-bad-1", "errors": [{"type": "string_too_short", "loc": ["claim"], "msg": "String should have at least 10 characters", "input": "too short", "ctx": {"min_length": 10}, "url": "https://errors.pydantic.dev/2.12/v/string_too_short"}, {"type": "string_too_short", "loc": ["baseline"], "msg": "String should have at least 3 characters", "input": "", "ctx": {"min_length": 3}, "url": "https://errors.pydantic.dev/2.12/v/string_too_short"}, {"type": "value_error", "loc": ["datasets"], "msg": "Value error, array contains empty/blank strings", "input": ["", "Dataset-A"], "ctx": {"error": "array contains empty/blank strings"}, "url": "https://errors.pydantic.dev/2.12/v/value_error"}, {"type": "string_too_short", "loc": ["primary_metric"], "msg": "String should have at least 2 characters", "input": "", "ctx": {"min_length": 2}, "url": "https://errors.pydantic.dev/2.12/v/string_too_short"}, {"type": "value_error", "loc": ["secondary_metrics"], "msg": "Value error, array contains empty/blank strings", "input": ["latency", ""], "ctx": {"error": "array contains empty/blank strings"}, "url": "https://errors.pydantic.dev/2.12/v/value_error"}, {"type": "greater_than_equal", "loc": ["budget_gpu_hours"], "msg": "Input should be greater than or equal to 1", "input": 0, "ctx": {"ge": 1}, "url": "https://errors.pydantic.dev/2.12/v/greater_than_equal"}, {"type": "less_than_equal", "loc": ["max_trials"], "msg": "Input should be less than or equal to 4", "input": 9, "ctx": {"le": 4}, "url": "https://errors.pydantic.dev/2.12/v/less_than_equal"}]}]

## Likely Causes
- Input JSON malformed or not UTF-8 encoded.
- Spec schema mismatch (missing required fields, wrong types, or out-of-range values).
- File I/O issue (missing path or permission denied).

## Mitigation Notes
1. Validate JSON shape before run: top-level list of objects.
2. Ensure each item includes required keys: hypothesis_id, claim, rationale, baseline, intervention, primary_metric.
3. Keep constraints in range: budget_gpu_hours >= 1, max_trials in [2,4], no blank dataset/metric values.
4. Re-run generator after fixing input and verify both markdown + json outputs exist.
