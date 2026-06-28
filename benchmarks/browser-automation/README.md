# Benchmark: Browser Automation

Navigate, scrape, and verify content across multiple web pages.

## Goal

Navigate, scrape, and verify content across multiple web pages.

## Success criteria

All target data extracted and verified against expected schema.

## Artifacts

- `scraped-data.json`
- `screenshots/`
- `verification.json`

## Budget

- **Cost:** $3
- **Runtime:** 10m

## Required capabilities

- `parse_loopfile`
- `run_loop`
- `verify`
- `tools_mcp`

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
infini run benchmarks/browser-automation/Loopfile.yaml --mock
infini inspect runs/latest/
```
