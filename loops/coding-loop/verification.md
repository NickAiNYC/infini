# Verification — coding-loop

How `coding-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `tests:pass`
- `pr-url.txt:valid_url`

## Semantic checks

- `judge:feature_completeness>=90`
- `judge:test_coverage>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `coding-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
