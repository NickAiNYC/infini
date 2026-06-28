# debug-loop

> *Canonical loop · draft*

The debug loop is where the Loop Engineer discipline is most visible. The reproducer must reproduce the bug BEFORE the fixer is allowed to touch code. Root-cause citation is mandatory — fixes without a cited cause don't ship.

## When to use

Use this loop when you need reproduce an open bug, isolate the root cause, propose a fix, and verify the fix does not regress other tests.

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
infini install infini/debug-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
