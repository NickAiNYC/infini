# Infinite Loops

## Smell

The loop runs forever. It never reaches `verified`, never hits
`budget_exceeded`, and never escalates. It just keeps iterating.

## Why it fails

Usually one of:

- `STOP_WHEN` is unreachable. The loop checks for `all_verify_passed`,
  but verification never passes — and there's no `iterations>=N` cap.
- The loop's verify block is contradictory. It can never pass.
- The loop's `BUDGET` is too high (or absent in development mode), so
  budget never aborts it.
- The loop is making progress but each iteration makes the situation
  *worse* — it's optimizing for the wrong thing.

The cost is money and time. A 6-iteration loop that should cost $5
becomes a 100-iteration loop that costs $80.

## Fix

- **Always cap iterations.** `STOP_WHEN: [all_verify_passed,
  iterations>=5]`. Five iterations is enough for most loops; if it
  hasn't shipped by then, something is wrong.
- **Always set a budget.** Even in development. `BUDGET: { dollars: 1,
  minutes: 5 }` is enough to catch runaway loops.
- **Inspect the trace.** `infini inspect runs/latest/` shows you what
  each iteration did. If iteration 5 is identical to iteration 4, the
  loop is stuck — it's not learning from its failures.
- **Check that verify can pass.** If your `VERIFY` block requires
  `judge:correctness>=99`, it probably can't. Lower the threshold and
  see if the loop converges.
- **Pair with [Budget Guard](../patterns/budget-guard.md).** Stop at 80%
  of budget, not 100%. Leave room for analysis.
