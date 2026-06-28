# Verification — migration-loop

How `migration-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `test-output.log:exit_zero`
- `behavior-diff.json:no_regressions`

## Semantic checks

- `judge:migration_completeness>=90`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `migration-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
