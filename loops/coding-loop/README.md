# coding-loop

> *Canonical loop · draft*

The canonical coding loop is the first loop most teams write. It is the 'hello world' of Loop Engineers: plan, edit, test, ship. The discipline lives in the VERIFY block — feature_completeness and test_coverage are not optional. Without them, you have a chain, not a loop.

## When to use

Use this loop when you need implement a feature described in a github issue, preserve all existing tests, and open a pull request.

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
infini install infini/coding-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
