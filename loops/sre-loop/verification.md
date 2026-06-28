# Verification — sre-loop

How `sre-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `root-cause.md:exists`
- `postmortem.signed.md:exists`

## Semantic checks

- `judge:root_citation>=85`
- `judge:references_prior_incidents>=1`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `sre-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
