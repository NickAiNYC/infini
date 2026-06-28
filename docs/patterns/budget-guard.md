# Budget Guard Pattern

## Problem

A loop is consuming budget faster than expected. You want to stop it
before it exhausts the budget entirely, leaving room for replay and
analysis.

## Diagram

```text
step → step → [BUDGET > 80%] → stop, save state, escalate
```

## Loopfile

```yaml
BUDGET: { dollars: 5, minutes: 15 }

STOP_WHEN:
  - all_verify_passed
  - "budget_remaining<20%"   # stop when ≤20% remains

ENGINE:
  type: hermes
  governance:
    budget_policy: strict
    escalation_policy: enabled
```

## Tradeoffs

**Gives:**
- Loops fail cheaply instead of expensively.
- Room to replay and debug after a budget-exceeded failure.

**Costs:**
- The loop might have shipped if it had a bit more budget. You'll never
  know.
- The 20% threshold is arbitrary; tuning it takes experimentation.

## Best practices

- **Set the threshold at 80% spent (20% remaining).** This leaves room
  for one more iteration, which is usually enough to either ship or fail
  cleanly.
- **Pair with `LESSONS`.** When the budget guard fires, append a lesson:
  "This loop hit 80% budget at iteration N. Consider raising the budget
  or splitting the loop."
- **Don't set the threshold too low.** Stopping at 50% spent wastes
  budget. The point is to fail *before* exhaustion, not to fail at the
  halfway mark.
- **Distinguish "budget_exceeded" from "verified."** The trace's
  `outcome` field makes this explicit. A loop that hit the budget guard
  did not ship; don't treat its artifacts as shipped.
- **Use `budget_policy: advisory` for development.** In development, you
  want to see how the loop fails, not have it aborted. In production,
  `strict` is the right default.
