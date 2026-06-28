# Benchmark: Refactoring

Refactor a module without changing observable behavior.

## Goal

Refactor a module without changing observable behavior.

## Success criteria

100% tests pass, behavior diff shows no changes, migration completeness ≥ 90%.

## Artifacts

- `src/`
- `test-output.log`
- `behavior-diff.json`

## Budget

- **Cost:** $4
- **Runtime:** 12m

## Required capabilities

- `parse_loopfile`
- `run_loop`
- `verify`

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
infini run benchmarks/refactoring/Loopfile.yaml --mock
infini inspect runs/latest/
```
