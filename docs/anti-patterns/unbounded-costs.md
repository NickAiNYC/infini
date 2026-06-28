# Unbounded Costs

## Smell

The Loopfile has no `BUDGET` block, or has one with absurdly high
ceilings (`dollars: 1000`).

## Why it fails

A loop without a budget is a loop that can spend forever. A stuck loop
spends $100 on retries before anyone notices. A loop with a $1000 budget
might spend $200 before its `iterations>=10` cap fires.

This is how teams get surprise AI bills. The model is cheap per call;
the loop is expensive per run.

## Fix

- **Every Loopfile must have a `BUDGET` block.** This is enforced by
  `infini validate`.
- **Start small.** `BUDGET: { dollars: 1, minutes: 5 }` is enough for
  most development. Scale up only when the loop consistently hits the
  cap and you understand why.
- **Set all three ceilings.** Dollars, minutes, and tokens. Any one can
  abort the loop. Tokens matter because they're a leading indicator of
  cost — a loop that's burning tokens fast is about to burn dollars.
- **Use `budget_policy: strict` in production.** `advisory` is for
  development only.
- **Pair with [Budget Guard](../patterns/budget-guard.md).** Stop at
  80% of budget, not 100%. Leave room for analysis.
- **Inspect cost per step.** `infini inspect runs/latest/` shows a cost
  waterfall. If one step consumes 60% of the budget, that's the step to
  optimize.
