# Verification — content-loop

How `content-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `final.md:exists`

## Semantic checks

- `judge:brand_tone>=85`
- `judge:quality>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `content-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
