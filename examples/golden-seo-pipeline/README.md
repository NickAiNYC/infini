# Golden Example: SEO Pipeline

> **The proof.** This Loopfile runs identically across multiple engines.
> Same YAML, same verification, same trace shape — different runtimes.

## The loop

An SEO content pipeline that researches keywords, drafts an article,
optimizes for the target keyword, verifies the content passes SEO and
quality checks, and produces a publish-ready article.

## Run it

```bash
# On the INFINI Reference Engine (mock mode — no API key needed)
infini run examples/golden-seo-pipeline/seo-loop.yaml --mock

# On Hermes (governance brain)
infini run examples/golden-seo-pipeline/seo-loop.yaml --engine hermes

# On OpenClaw (execution runtime)
infini run examples/golden-seo-pipeline/seo-loop.yaml --engine openclaw

# Inspect the trace in the Observatory
infini ui runs/latest/run.json
```

The **exact same YAML** runs on all three engines. That's the portability
layer. That's the point.

## Why this is a "golden" example

- **Portable.** Uses only spec-defined features. No engine-specific assumptions.
- **Verified.** Two-tier verification: syntactic (word count, keyword density) + semantic (content quality, SEO score).
- **Bounded.** $4 / 15m budget. Stops when verified or after 3 iterations.
- **Inspectable.** Produces a `run.json` trace the Observatory can render in 3D.
- **Replayable.** `infini replay runs/latest/ --step s3` to time-travel.

## Files

- [`seo-loop.yaml`](seo-loop.yaml) — the Loopfile
- [`expected-output.md`](expected-output.md) — what a verified run produces
- [`README.md`](README.md) — this file
