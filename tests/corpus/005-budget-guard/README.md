# Corpus 005: budget-guard

Tight budget that forces the loop to stop before completion. Tests budget enforcement.

## Metadata

- **Category tags:** `budget`, `safety`
- **Required capabilities:** `parse_loopfile`, `run_loop`, `budget`
- **Budget:** $1 / 2m
- **Max iterations:** 1

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
