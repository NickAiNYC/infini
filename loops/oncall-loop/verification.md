# Verification — oncall-loop

How `oncall-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `triage.md:exists`
- `proposal.md:exists`
- `handoff.md:exists`

## Semantic checks

- `judge:triage_quality>=85`
- `judge:proposal_safety>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `oncall-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
