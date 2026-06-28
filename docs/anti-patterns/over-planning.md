# Over-Planning

## Smell

The `plan` step costs more than the `execute` step. The plan is 2000
words. The plan is more detailed than the final output.

## Why it fails

Planning has a cost. A plan that's 10x more detailed than the task
requires is wasted budget. The loop spends $2 producing a plan and $0.50
executing it.

Over-planning also slows the loop. A 5-minute plan step for a 30-second
execution step is a 6x slowdown.

## Fix

- **Match the plan's depth to the task's complexity.** A one-file change
  needs a one-paragraph plan. A multi-file refactor needs a multi-page
  plan. Don't write the latter for the former.
- **Cap the plan step's budget.** `STEPS: [{ id: s1, name: plan, ...,
  budget: { dollars: 0.50, minutes: 2 } }]`. If the plan step exceeds
  its budget, it stops planning and ships what it has.
- **Use a cheaper model tier for planning.** `haiku` for simple plans,
  `sonnet` for complex, `opus` only for architecture-level planning.
- **Inspect the plan.** `infini inspect` shows the plan as an artifact.
  If it's longer than the final output, you're over-planning.
- **Iterate on the plan, not just the execution.** If the executor fails
  because the plan was wrong, the next iteration should produce a *new*
  plan, not just retry the execution with the same plan.
- **Pair with [Memory Update](../patterns/memory-update.md).** If the
  plan step keeps producing the same plan, your lessons file should
  capture that. Future runs can skip detailed planning and use the
  cached plan.
