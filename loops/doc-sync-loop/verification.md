# Verification — doc-sync-loop

How `doc-sync-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `doc-gaps.json:empty_after_sync`
- `sync-check.json:all_synced`

## Semantic checks

- `judge:doc_accuracy>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `doc-sync-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
