# Benchmark: Coding

Implement a feature from a GitHub issue, preserve tests, open a PR.

## Goal

Implement a feature from a GitHub issue, preserve tests, open a PR.

## Success criteria

Tests pass, PR opened, feature completeness ≥ 90%.

## Artifacts

- `src/`
- `test-output.log`
- `pr-url.txt`

## Budget

- **Cost:** $5
- **Runtime:** 15m

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
infini run benchmarks/coding/Loopfile.yaml --mock
infini inspect runs/latest/
```
