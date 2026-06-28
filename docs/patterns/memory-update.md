# Memory Update Pattern

## Problem

A loop just ran. It learned something. You want future runs of the same
loop to benefit from that learning.

## Diagram

```text
... → final_step → [APPEND LESSON] → ship
```

## Loopfile

```yaml
LESSONS: { path: memory/coding-loop.md, append: true }
```

The `LESSONS` block declares where lessons are stored. After every run,
the engine appends a lesson. Before every run, the engine reads recent
lessons into the planner's context.

## Tradeoffs

**Gives:**
- Loops that improve with each run.
- A durable record of what the loop has learned.

**Costs:**
- Lessons accumulate. Without curation, the file becomes noise.
- Stale lessons mislead. The loop needs a decay policy (v1.1).

## Best practices

- **Append, don't edit.** Lessons are append-only. If a lesson is wrong,
  append a correction. Editing memory is a human action.
- **Be specific.** "Tests failed because of a missing import in
  `src/auth.py`" is a lesson. "Be careful" is not.
- **Include failures.** A lessons file with only successes doesn't teach.
  Failed runs produce the most valuable lessons.
- **Read before plan.** The first step of every loop should be a `recall`
  step that reads recent lessons. A loop that doesn't recall is a loop
  that doesn't learn.
- **Cap the lesson count.** v1.0 doesn't enforce a cap; v1.1's `MEMORY`
  block will. For now, manually prune old lessons quarterly.
- **Pair with [Self Improvement](self-improvement.md).** A loop that
  updates its own Loopfile based on lessons is the ultimate form of this
  pattern. Use with caution.
