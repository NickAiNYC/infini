# Corpus 002: research-summary

Multi-source research with citation verification. Tests browser tools and semantic verification.

## Metadata

- **Category tags:** `research`, `verification`
- **Required capabilities:** `parse_loopfile`, `run_loop`, `verify`
- **Budget:** $6 / 20m
- **Max iterations:** 3

## Files

- [`Loopfile.yaml`](Loopfile.yaml) — the loop definition
- [`expected.json`](expected.json) — expected trace shape + required capabilities
- [`README.md`](README.md) — this file

## Run it

```bash
infini validate Loopfile.yaml
infini run Loopfile.yaml --mock
infini inspect runs/latest/
```

## Why this case exists

This corpus case is part of INFINI's canonical benchmark suite — the
"ImageNet for agent loops." Every engine should run these. Every release
should run these. The corpus is durable; it does not change between
releases except to fix bugs or add new cases.
