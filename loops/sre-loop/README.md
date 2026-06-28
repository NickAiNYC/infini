# sre-loop

> *Canonical loop · draft*

The SRE loop is the oncall loop's bigger sibling. It investigates patterns across incidents, not single incidents. The references_prior_incidents check forces the loop to use memory — without it, every incident is treated as new and the loop never learns.

## When to use

Use this loop when you need investigate a recurring incident, identify a root cause, propose a permanent fix, and generate a postmortem.

## When NOT to use

- If your task is one-shot and doesn't need verification, write a single prompt instead.
- If your task is interactive and requires human input mid-execution, use a workflow, not a loop.
- If your task doesn't have a clear "done" condition, you don't have a loop yet — figure that out first.

## Files

- [`Loopfile.yaml`](Loopfile.yaml) — the loop itself
- [`essay.md`](essay.md) — long-form discussion *(draft)*
- `fixtures/` — fixture sets for CI *(planned)*
- `expected/` — expected trace shape *(planned)*

## Run it

```bash
infini install infini/sre-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
