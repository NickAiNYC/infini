# Verification — debug-loop

How `debug-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `repro.log:bug_reproduced`
- `test-output.log:bug_fixed`

## Semantic checks

- `judge:root_cause_cited>=90`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `debug-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
