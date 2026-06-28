# Corpus 008: tool-call-placeholder

Loop that declares MCP tools. Tests tool resolution and namespacing (placeholder — no real MCP server).

## Metadata

- **Category tags:** `tools`, `mcp`
- **Required capabilities:** `parse_loopfile`, `run_loop`, `tools_mcp`
- **Budget:** $3 / 8m
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
