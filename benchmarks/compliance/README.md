# Benchmark: Compliance

Audit claims against policy with escalation on low confidence.

## Goal

Audit claims against policy with escalation on low confidence.

## Success criteria

All claims checked, audit trail signed, escalation triggered on < 80% confidence.

## Artifacts

- `audit.json`
- `decision.md`
- `audit/log.jsonl`

## Budget

- **Cost:** $4
- **Runtime:** 12m

## Required capabilities

- `parse_loopfile`
- `run_loop`
- `verify`
- `memory`

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
infini run benchmarks/compliance/Loopfile.yaml --mock
infini inspect runs/latest/
```
