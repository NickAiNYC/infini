# RFC-0002: Verification Model

- Start date: 2026-06-28
- Status: implemented
- Spec version: 1.0
- PR: #1
- Implementation: shipped in `infini 1.0.0`

## Summary

Defines how a Loopfile declares what "done" means and how an engine checks
it. Verification is split into syntactic (deterministic) and semantic
(model-judged) checks. Both must pass for a loop to ship.

## Motivation

Without verification, a loop is a chain that happens to repeat. The single
biggest failure mode in agent systems is shipping unverified work — the
model said it was done, so it must be done.

Verification must be:

- **Declared up front.** If you don't know what "done" looks like, you
  don't have a loop.
- **Two-tiered.** Syntactic checks (did the test pass? is the file valid
  JSON?) are deterministic and cheap. Semantic checks (is this answer
  correct? is this code well-structured?) are model-judged and produce a
  confidence score. Both are required.
- **Bounded by confidence.** A semantic check that returns 70% confidence
  is not a pass. The threshold is declared per-loop.

## Detailed design

The `VERIFY` block:

```yaml
VERIFY:
  syntactic:
    - "tests:pass"
    - "lint"
    - "greetings.json:valid_json"
  semantic:
    - "judge:correctness>=90"
    - "rubric:accessibility>=85"
  confidence_threshold: 85
```

### Syntactic checks

A syntactic check is a string of the form `<target>:<predicate>` or a bare
command name. The engine resolves the check to a deterministic evaluation:

- `<file>:<predicate>` — checks a file. Predicates: `exists`, `non_empty`,
  `valid_json`, `valid_yaml`, `exit_zero` (for log files).
- `<command>` — runs a shell command. Exit code 0 is pass; anything else
  is fail.

Syntactic checks must be deterministic. If a check is non-deterministic
(e.g., "the output looks good"), it belongs in `semantic`.

### Semantic checks

A semantic check is a string of the form `<judge>:<rubric><comparator><value>`:

- `judge:correctness>=90` — a model-judged correctness score, 0–100.
- `rubric:accessibility>=85` — a rubric-based score, 0–100.
- `judge:any_string` — any model-judged check the engine knows how to run.

Semantic checks produce a confidence score from 0 to 100. The check passes
if the score meets the comparator.

### Confidence threshold

`confidence_threshold` is the minimum mean confidence across all semantic
checks for the loop to be considered *verified*. A loop where every
semantic check passes its individual comparator but the mean is below
threshold is **not** verified.

This catches the failure mode where individual checks pass marginally but
the loop overall is weak.

### Outcome

A loop's outcome is one of:

| Outcome | Meaning |
| --- | --- |
| `verified` | All syntactic checks pass; all semantic checks pass their comparators; mean confidence ≥ threshold. |
| `unverified` | Some checks failed. The loop did not ship. |
| `budget_exceeded` | The loop was aborted by BUDGET. |
| `escalated` | The loop paused for human review (Hermes governance only). |
| `error` | The engine itself failed. |

Only `verified` ships artifacts.

## Alternatives considered

- **Single-tier verification (only semantic).** Rejected — syntactic checks
  are cheap, deterministic, and catch obvious failures before spending
  tokens on semantic checks.
- **Single-tier verification (only syntactic).** Rejected — most real
  "is this correct?" questions can't be answered by exit codes.
- **No confidence threshold.** Rejected — without it, a loop where every
  check barely passes ships with false confidence.
- **Per-check thresholds only (no global mean).** Rejected — the global
  mean catches weak overall loops that pass individual checks marginally.

## Backwards compatibility

v1.0. No prior version.

## Conformance impact

The `Verify` conformance capability requires the engine to:

1. Run every `syntactic` check and report pass/fail per check.
2. Run every `semantic` check and report confidence per check.
3. Compute the mean confidence across semantic checks.
4. Mark the loop `verified` only if all checks pass and the mean ≥ threshold.

Partial conformance (syntactic only, or semantic only) is allowed and
tracked in [`compatibility.md`](../compatibility.md).

## Open questions

- Should the threshold be a per-check field instead of a global mean?
  Current answer: global mean, simpler. Revisit if real loops need per-check.
- Should `judge:` and `rubric:` be a registry-defined enum? Current answer:
  engine-resolved. Revisit at v1.1.

## Future possibilities

- v1.1: `HOOKS:` block to declare pre-verify and post-verify hooks.
- v1.2: typed predicates (`{kind: file, path: ..., predicate: exists}`
  instead of strings).
- v2.0: declarative verification DSL, replacing the string format.

## Acknowledgements

The two-tier model is borrowed from compiler design (syntactic vs. semantic
analysis) and from the SRE Book (separating "did it run?" from "is it
correct?").
