# Fan Out Pattern

## Problem

You have one input and N sub-tasks derived from it. Each sub-task is
independent. Run them in parallel.

This is the [Parallel Workers](parallel-workers.md) pattern when the
number of workers is determined by the input, not by the Loopfile.

## Diagram

```text
input → split → ┬─ sub_1 ─┐
                 ├─ sub_2 ─┤
                 ├─ sub_3 ─┤
                 └─ sub_N ─┴─ merge
```

## Loopfile

Fan out is a runtime concept. The Loopfile declares a `split` step that
produces N artifacts, and a `merge` step that depends on whatever the
split produced.

```yaml
STEPS:
  - { id: s1, name: input,  action: read_input,   uses: builder, produces: [input.json] }
  - { id: s2, name: split,  action: fan_out_split, uses: planner, depends_on: [s1], produces: [subtasks/*.json] }
  - { id: s3, name: process, action: fan_out_process, uses: builder, depends_on: [s2], produces: [results/*.json] }
  - { id: s4, name: merge,  action: fan_out_merge, uses: planner, depends_on: [s3], produces: [merged.json] }
```

The `fan_out_split` action produces a directory of subtask files; the
`fan_out_process` action runs one worker per subtask; the `fan_out_merge`
action combines them.

## Tradeoffs

**Gives:**
- Parallelism without knowing N at Loopfile-authoring time.
- Scales with the input size.

**Costs:**
- More complex than [Parallel Workers](parallel-workers.md). The engine
  has to manage dynamic worker counts.
- Cost is unbounded by the input size. A 1000-item input means 1000
  workers. Cap this in the engine config.

## Best practices

- **Cap the worker count.** Most engines will refuse to spawn 1000
  parallel model calls. Set a sensible cap (e.g., 10) and process in
  batches.
- **Make split deterministic.** The split should produce the same
  subtasks for the same input. Non-deterministic splits make replay
  impossible.
- **Number subtasks.** `subtasks/001.json`, `subtasks/002.json`, etc.
  This makes the merge step's job easier.
- **Handle partial failures.** If 5 of 100 subtasks fail, do you fail
  the loop or ship partial results? Make this explicit in the merge
  step's action.
