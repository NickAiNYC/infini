# migration-loop

> *Canonical loop · draft*

Migration loops are where teams lose weeks. The behavior-diff check is the floor; the migration_completeness semantic check is the ceiling. Both must pass before the loop ships.

## When to use

Use this loop when you need migrate a named module from one framework version to another, preserving behavior and updating tests.

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
infini install infini/migration-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
