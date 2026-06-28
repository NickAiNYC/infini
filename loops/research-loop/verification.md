# Verification — research-loop

How `research-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `research_brief.md:every_claim_has_citation`

## Semantic checks

- `judge:source_quality>=85`
- `judge:answer_quality>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `research-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
