# Verification — review-loop

How `review-loop` declares what "done" means and how it checks it.

## Syntactic checks

- `review.md:rubric_complete`
- `comment-url.txt:valid_url`

## Semantic checks

- `judge:cross_check_agreement>=80`

## Confidence threshold

85

## Why these checks

Each verifier catches a real failure mode of `review-loop`. See the
loop's [essay](essay.md) for the reasoning.

## Inspecting verification

```bash
infini inspect runs/latest/   # open the Observatory, click "Verification"
```

The Observatory shows each check's status, confidence score, and
threshold. Failed checks expand to show why.
