# Benchmark: Planning

Break down a complex task into an executable plan with dependencies.

## Goal

Break down a complex task into an executable plan with dependencies.

## Success criteria

Plan covers all requirements, dependencies are acyclic, plan is executable.

## Artifacts

- `plan.md`
- `task-graph.json`
- `estimates.json`

## Budget

- **Cost:** $2
- **Runtime:** 8m

## Required capabilities

- `parse_loopfile`
- `run_loop`

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
infini run benchmarks/planning/Loopfile.yaml --mock
infini inspect runs/latest/
```
