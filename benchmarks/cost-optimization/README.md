# Benchmark: Cost Optimization

Complete a task within a tight budget, optimizing token usage.

## Goal

Complete a task within a tight budget, optimizing token usage.

## Success criteria

Task completes within budget, cost per step < $0.50, no retries exhausted.

## Artifacts

- `output.txt`
- `cost-breakdown.json`
- `optimization-report.md`

## Budget

- **Cost:** $1
- **Runtime:** 5m

## Required capabilities

- `parse_loopfile`
- `run_loop`
- `budget`

## Verification rubric

| Check | Type | Threshold |
| --- | --- | --- |
| Artifacts exist | syntactic | all listed artifacts present |
| Output quality | semantic | ≥ 85 |
| Budget respected | syntactic | spent ≤ declared |
| No retries exhausted | syntactic | retry_attempt < max |

## Expected outputs

A successful benchmark run produces a trace with:
- `outcome: verified`
- All syntactic checks pass
- All semantic checks pass with confidence ≥ 85
- Budget within limits
- All artifacts present

## Running

```bash
infini run benchmarks/cost-optimization/Loopfile.yaml --mock
infini inspect runs/latest/
```
