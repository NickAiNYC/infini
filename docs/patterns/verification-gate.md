# Verification Gate Pattern

## Problem

You want to verify the output of a step before moving on, instead of
waiting until the end of the loop. This catches failures early, when
they're cheap to fix.

## Diagram

```text
produce → [VERIFY GATE] → pass → continue
                    └─→ fail → retry or escalate
```

## Loopfile

```yaml
STEPS:
  - { id: s1, name: produce,  action: write_code,    uses: coder,  produces: [src/auth.py] }
  - { id: s2, name: gate,     action: verify_output, uses: auditor, depends_on: [s1], produces: [gate-result.json] }
  - { id: s3, name: next,     action: write_tests,   uses: coder,  depends_on: [s2], produces: [tests/auth_test.py] }

VERIFY:
  syntactic:
    - "src/auth.py:exists"
    - "tests/auth_test.py:exists"
    - "gate-result.json:passed"
```

The `gate` step is itself a verification. It runs immediately after the
produce step, not at the end of the loop.

## Tradeoffs

**Gives:**
- Failures caught early, when they're cheap.
- The downstream step can assume its input is verified.

**Costs:**
- More steps = more overhead.
- If the gate is too strict, the loop iterates endlessly on a step that
  would have passed the final verify.

## Best practices

- **Use gates for expensive downstream steps.** If `s3` costs $1 to run,
  gating `s2` is worth it. If `s3` costs $0.01, don't bother.
- **Gates are not a replacement for final verification.** They're a
  supplement. The final `VERIFY` block is still required.
- **Make the gate's check specific.** "Does the file parse?" is a good
  gate. "Is the code good?" is too vague — save that for the final
  verify.
- **Don't gate every step.** A loop with 8 steps and 8 gates is a loop
  that spends half its budget on gating. Gate the high-leverage points.
- **Pair with [Retry](retry.md).** When a gate fails, retry the produce
  step, not the gate.
