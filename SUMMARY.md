# Loom

Loom is the open standard for agent loops. This directory mirrors the [main repo](https://github.com/loom-spec/loom).

## What's here

- `spec/` — the Loopfile, trace, and state format contracts
- `loops/` — 12 canonical loops
- `cli/` — the reference CLI (`loom`)
- `prompts/` — the Loop Engineer operating prompt
- `registry/` — RFC for the loop registry
- `docs/` — architecture, usage, community, examples
- `verification/` — rubric, judge prompt, test plan, external checks
- `state/` — template state files (loop_state.json, memory.json, etc.)
- `.github/workflows/` — `loom ci` GitHub Action
- `MANIFESTO.md` — *Loops > Chains*
- `README.md` — start here
- `LICENSE` — MIT
- `CONTRIBUTING.md` — how to contribute
- `CHANGELOG.md` — what changed
- `CONTRIBUTORS.md` — who helped

## Quickstart

```bash
pip install -e cli/
loom validate loops/coding-loop.yaml
loom run loops/coding-loop.yaml
loom inspect runs/run_*/
```

See `README.md` for the full pitch.
