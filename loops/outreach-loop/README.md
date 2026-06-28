# outreach-loop

> *Canonical loop · draft*

Outreach at scale is the loop most likely to produce spam. The personalization_check is the discipline: if the verifier can guess which template a draft came from, it's not personalized. The loop fails the verification and the writer tries again.

## When to use

Use this loop when you need generate personalized outreach for a list of recipients, verify each is non-generic, and produce sendable drafts.

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
infini install infini/outreach-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
