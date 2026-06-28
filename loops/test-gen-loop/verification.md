# Verification — test-gen-loop

How `test-gen-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `tests/new/:non_empty`
- `test-output.log:exit_zero`
- `coverage.json:target_reached`

## Semantic checks

- `judge:test_quality>=85`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `test-gen-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
