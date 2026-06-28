# Verification

Chapter 4 of the [INFINI Handbook](README.md).

> Verification is the heart of Loop Engineering. Without it, you have a
> chain, not a loop.

---

## Why verify

The single biggest failure mode in agent systems is shipping unverified
work. The model said it was done, so it must be done.

This is the same failure mode that gave us tests in software engineering.
You don't trust the code; you trust the tests. In Loop Engineering, you
don't trust the model; you trust the verifiers.

The difference: software tests are written by humans. Loop verifiers can
be a mix of human-written checks (`tests:pass`) and model-judged checks
(`judge:correctness>=90`). Both are required.

---

## Two tiers

INFINI splits verification into two tiers:

### Syntactic checks

Deterministic. Cheap. Run before semantic checks.

```yaml
VERIFY:
  syntactic:
    - "tests:pass"
    - "lint"
    - "greetings.json:valid_json"
    - "src/dark-mode.tsx:exists"
```

A syntactic check is one of:

- `<file>:<predicate>` — checks a file. Predicates: `exists`,
  `non_empty`, `valid_json`, `valid_yaml`, `exit_zero` (for log files).
- `<command>` — runs a shell command. Exit code 0 is pass.

Syntactic checks must be deterministic. If a check is non-deterministic
("the output looks good"), it belongs in `semantic`.

### Semantic checks

Model-judged. More expensive. Run after syntactic checks pass.

```yaml
VERIFY:
  semantic:
    - "judge:correctness>=90"
    - "rubric:accessibility>=85"
    - "judge:policy_citation>=90"
```

A semantic check is `<judge>:<rubric><comparator><value>`:

- `judge:correctness>=90` — a model-judged correctness score, 0-100.
- `rubric:accessibility>=85` — a rubric-based score, 0-100.

Semantic checks produce a confidence score from 0 to 100. The check
passes if the score meets the comparator.

### The confidence threshold

```yaml
VERIFY:
  confidence_threshold: 85
```

`confidence_threshold` is the minimum mean confidence across all semantic
checks for the loop to be considered *verified*. A loop where every
semantic check passes its individual comparator but the mean is below
threshold is **not** verified.

This catches the failure mode where individual checks pass marginally but
the loop overall is weak. A loop with three checks scoring 86, 87, and 84
passes each individually (against `>=80`) but has a mean of 85.67 — which
fails an 85 threshold? No, that passes. But against an 86 threshold, it
fails. The threshold is the overall quality bar.

---

## The four verifier failure modes

Verifiers themselves can fail. Watch for these:

### 1. The sycophant

A verifier that always returns 90+. It's worse than no verifier — it
gives false confidence. Tune your verifiers against real failures. If
your verifier has never failed, it's not a verifier.

### 2. The nitpicker

A verifier that fails on trivial issues. The loop spends its budget
fixing comments instead of features. Lower the threshold or rewrite the
rubric.

### 3. The slow judge

A verifier that takes 30 seconds per check. With 5 checks across 6
iterations, that's 15 minutes of verifier time. Use cheaper models for
semantic checks (`haiku` tier); reserve `opus` for the most important
checks.

### 4. The liar

A verifier that passes work a human would reject. This is the hardest to
catch. The defense is the [`review-loop`](../../loops/review-loop/) — a
second model judges the verifier's judgment. Cross-check agreement is
itself a verification.

---

## Writing good verifiers

### Start with syntactic

Every loop should have at least one syntactic check. "Does the file
exist?" is a surprisingly effective filter. Many loops fail at this
stage, before any tokens are spent on semantic checks.

### Make semantic checks specific

`judge:correctness>=90` is a starting point. `judge:tests_cover_edge_cases>=85`
is better. The more specific the rubric, the less room the judge has to
be a sycophant.

### Use multiple judges for high-stakes loops

For loops where being wrong is expensive (compliance, security, healthcare),
use two semantic judges and require both to pass. The
[`review-loop`](../../loops/review-loop/) pattern formalizes this.

### Set the threshold honestly

If you set `confidence_threshold: 95` and your verifiers rarely score
above 90, your loop will iterate forever. Start at 80, run the loop, see
what scores you actually get, then tune.

### Verify the verifiers

Run `infini inspect` on a verified run. Look at the verifier outputs.
Would you have shipped this work? If not, your verifiers are too lenient.

---

## When verification is wrong

Sometimes the verifier is right and the loop is wrong. Sometimes the
verifier is wrong and the loop is right. The discipline is knowing which
is which.

If your loop fails verification but you believe the output is correct:

1. Don't weaken the verifier to make the loop pass. That's how you ship
   bad work.
2. Don't ship the loop unverified. That's how you ship untrusted work.
3. Add a `judge:human_review_required` check that escalates to a human.
   The human decides. This is the Hermes governance pattern.

See [Chapter 8, Governance](governance.md), for the escalation pattern.

---

## What's next

- Chapter 5, [Memory](memory.md) — loops that learn.
- For the normative spec, see [`spec/rfcs/RFC-0002-verification.md`](../../spec/rfcs/RFC-0002-verification.md).
- For verification patterns, see [`docs/patterns/verification-gate.md`](../patterns/verification-gate.md).
