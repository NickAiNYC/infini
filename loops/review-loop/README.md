# review-loop

> *Canonical loop · draft*

Two reviewers because one reviewer is a single point of failure. The cross_check_agreement score catches sycophantic agreement — if both reviewers say the same thing without independent reasoning, the score drops and the loop escalates.

## When to use

Use this loop when you need review a pull request against a declared rubric, cross-check findings with a second reviewer, and post a structured review.

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
infini install infini/review-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
