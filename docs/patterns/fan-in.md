# Fan In Pattern

## Problem

You have N parallel outputs. You need to combine them into one. This is
the second half of [Fan Out](fan-out.md) or
[Parallel Workers](parallel-workers.md).

## Diagram

```text
        ┌── worker_a ──┐
input ──┼── worker_b ──┼── fan_in → merged
        └── worker_c ──┘
```

## Loopfile

```yaml
STEPS:
  - { id: s3, name: fan_in, action: merge_results, uses: planner, depends_on: [s2a, s2b, s2c], produces: [merged.json] }

VERIFY:
  syntactic:
    - "merged.json:valid_json"
    - "merged.json:contains_all_inputs"
  semantic:
    - "judge:merge_quality>=85"
```

## Tradeoffs

**Gives:**
- One coherent output from many parallel inputs.
- A natural verification point.

**Costs:**
- The merge step is a single point of failure. If it's wrong, all the
  parallel work is wasted.
- Merge logic can be complex. Deciding how to combine conflicting
  outputs is a real design problem.

## Best practices

- **Verify the merge.** The merge step is where parallel outputs become a
  single artifact. This is a high-leverage verification point. Don't
  skip it.
- **Handle conflicts explicitly.** What if `worker_a` says "yes" and
  `worker_b` says "no"? The merge step's action must decide: majority
  vote, weighted by confidence, or escalate to a human.
- **Preserve provenance.** `merged.json` should record which worker
  produced which part. This is essential for debugging.
- **Don't merge too early.** If you can verify the parallel outputs
  independently, do that *before* merging. Failing fast on a bad worker
  is cheaper than merging garbage and then verifying.
- **Pair with [Reflection Loop](reflection-loop.md).** After merging,
  have a reflection step critique the merge. This catches merge logic
  errors.
