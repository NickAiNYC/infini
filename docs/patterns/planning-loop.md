# Planning Loop Pattern

## Problem

A complex task is too big to execute in one step. Plan first, then
execute the plan. This makes the loop's behavior legible to humans and
gives the executor a clear specification.

## Diagram

```text
plan → [plan verified?] → execute → verify → [ship or iterate]
```

## Loopfile

```yaml
STEPS:
  - { id: s1, name: plan,    action: coding.plan,    uses: planner, produces: [plan.md] }
  - { id: s2, name: execute, action: coding.execute, uses: coder,   depends_on: [s1], produces: [src/] }
  - { id: s3, name: test,    action: terminal.run,   uses: tester,  depends_on: [s2], produces: [test-output.log] }

VERIFY:
  syntactic:
    - "plan.md:exists"
    - "src/:exists"
    - "test-output.log:exit_zero"
  semantic:
    - "judge:plan_followed>=85"      # the execute step followed the plan
    - "judge:feature_completeness>=90"
  confidence_threshold: 85
```

## Tradeoffs

**Gives:**
- Human-readable artifact (`plan.md`) that explains what the loop is
  about to do.
- A natural verification point: did the executor follow the plan?

**Costs:**
- The plan step costs money and time. For simple tasks, planning is
  overhead.
- If the plan is wrong, the executor faithfully implements a wrong plan.

## Best practices

- **Make the plan a real artifact.** `plan.md` should be a document a
  human can read and review. If it's a one-liner, you didn't plan; you
  generated a TODO.
- **Verify that the executor followed the plan.** `judge:plan_followed>=85`
  catches executors that ignore the plan and wing it.
- **Don't over-plan.** A 2000-word plan for a one-file change is
  over-planning. Match the plan's depth to the task's complexity.
- **Iterate on the plan, not just the execution.** If the executor fails
  because the plan was wrong, the next iteration should produce a new
  plan, not just retry the execution.
- **Pair with [Memory Update](memory-update.md).** Append the plan to the
  lessons file. Future runs can reference prior plans for similar tasks.
