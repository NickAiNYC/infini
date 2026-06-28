# Benchmark: Research

Answer a research question with at least 3 cited primary sources.

## Goal

Answer a research question with at least 3 cited primary sources.

## Success criteria

Every claim cited, citations verified, source quality ≥ 85%.

## Artifacts

- `sources.json`
- `claims.json`
- `research_brief.md`

## Budget

- **Cost:** $6
- **Runtime:** 20m

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
infini run benchmarks/research/Loopfile.yaml --mock
infini inspect runs/latest/
```
