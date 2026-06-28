# Parallel Workers Pattern

## Problem

You have N independent tasks. Running them sequentially wastes time. Run
them in parallel.

## Diagram

```text
        ┌── worker_a ──┐
input ──┼── worker_b ──┼── merge
        └── worker_c ──┘
```

## Loopfile

```yaml
STEPS:
  - { id: s1, name: input,    action: read_input,   uses: builder, produces: [input.json] }
  - { id: s2a, name: worker_a, action: process,     uses: builder, depends_on: [s1], produces: [a.json] }
  - { id: s2b, name: worker_b, action: process,     uses: builder, depends_on: [s1], produces: [b.json] }
  - { id: s2c, name: worker_c, action: process,     uses: builder, depends_on: [s1], produces: [c.json] }
  - { id: s3, name: merge,    action: merge_results, uses: builder, depends_on: [s2a, s2b, s2c], produces: [merged.json] }
```

The engine sees that `s2a`, `s2b`, and `s2c` all depend only on `s1` and
executes them concurrently.

## Tradeoffs

**Gives:**
- Wall-clock time drops from `3 × T` to `T` (plus merge overhead).
- Independent failures don't block other workers.

**Costs:**
- Token cost is the same (you still do 3 units of work).
- Concurrency adds complexity. If workers share state, you have a
  coordination problem.

## Best practices

- **Workers must be truly independent.** If `worker_b` needs `worker_a`'s
  output, they're not parallel — they're sequential. Use `depends_on`.
- **Cap concurrency.** Most engines have a concurrency limit. Set it
  explicitly to avoid overwhelming the model API.
- **Merge defensively.** If one worker fails, the merge step needs to
  decide: fail the loop, use partial results, or retry the failed worker.
  Make this explicit in the merge step's action.
- **Verify each worker independently.** Don't wait until the merge to
  discover that `worker_b` produced garbage. Add a `VERIFY` check per
  worker artifact.
