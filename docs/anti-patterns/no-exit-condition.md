# No Exit Condition

## Smell

`STOP_WHEN` is technically present, but none of its predicates can
actually be reached. The loop runs until budget exhaustion every time.

Examples:
- `STOP_WHEN: [all_verify_passed]` — but verify never passes.
- `STOP_WHEN: [confidence>=95]` — but the verifier rarely scores above
  90.
- `STOP_WHEN: [iterations>=10]` — but `BUDGET` is so low that the loop
  hits budget before iteration 10.

## Why it fails

A loop with no reachable exit condition is a loop that always fails. It
never ships; it always exhausts budget. The team learns to ignore the
loop's output ("oh, it failed again") and the loop becomes noise.

## Fix

- **Always include `iterations>=N` as a backstop.** Even if you expect
  `all_verify_passed` to fire first, `iterations>=5` guarantees the
  loop terminates.
- **Check that verify can pass.** Run the loop once with
  `confidence_threshold: 0` to see what scores you actually get. If the
  scores are 70-80, a 90 threshold is unreachable.
- **Lower the threshold, then tune up.** Start at 75. If the loop
  consistently ships at 80, raise to 85. If it never ships, lower to
  75. Don't guess.
- **Inspect the trace.** `infini inspect` shows the verify results per
  iteration. If iteration 5's verify scores are lower than iteration
  1's, the loop is getting worse, not better. Something is wrong with
  the loop's logic, not the exit condition.
- **Use [Budget Guard](../patterns/budget-guard.md).** Stop at 80% of
  budget. This gives you room to inspect and debug, rather than hitting
  a hard budget stop.
- **Don't ship just because the loop stopped.** `STOP_WHEN: [iterations>=5]`
  means "stop after 5 iterations," not "ship after 5 iterations." The
  loop only ships if `all_verify_passed` fires. If it stops because of
  the iteration cap, it didn't ship.
