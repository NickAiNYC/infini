# research-loop

> *Canonical loop · draft*

The research loop is where hallucination is the failure mode. The every_claim_has_citation syntactic check is the hard floor. The semantic source_quality check is the soft floor. Together they make the loop usable for work where being wrong is expensive.

## When to use

Use this loop when you need answer a research question using at least three primary sources, with every claim cited and citations verified.

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
infini install infini/research-loop@0.1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

## Status

Draft. The Loopfile is spec-valid; the essay and fixtures are in progress.
