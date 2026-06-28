# Benchmark: Hybrid Agent

Hermes governs, OpenClaw executes — same Loopfile, two engines.

## Goal

Hermes governs, OpenClaw executes — same Loopfile, two engines.

## Success criteria

Governance audit signed, execution artifacts produced, both traces present.

## Artifacts

- `governance.json`
- `execution.json`
- `combined-trace.json`

## Budget

- **Cost:** $6
- **Runtime:** 18m

## Required capabilities

- `parse_loopfile`
- `run_loop`
- `verify`
- `inspect_trace`

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
infini run benchmarks/hybrid-agent/Loopfile.yaml --mock
infini inspect runs/latest/
```
