# Verification — outreach-loop

How `outreach-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `outreach-drafts/:non_empty`
- `personalization-check.json:all_personalized`

## Semantic checks

- `judge:personalization>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `outreach-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
