# Corpus 009: human-approval-gate

Loop that pauses for human approval before an irreversible step. Tests escalation.

## Metadata

- **Category tags:** `governance`, `human-in-loop`
- **Required capabilities:** `parse_loopfile`, `run_loop`, `verify`
- **Budget:** $4 / 15m
- **Max iterations:** 2

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
