# Replay — coding-loop

How to debug `coding-loop` using `infini replay`.

## Inspect the trace

```bash
infini inspect runs/latest/
```

Opens the Observatory. Click any step to see its input state, output
state, cost, and tool calls.

## Replay from a step

```bash
infini replay runs/latest/ --step s2
```

Restores state to just before `edit` (s2), opens an interactive
session. You can:

- Inspect the input state.
- Mutate the step's parameters.
- Resume execution from s2 forward.

The replay produces a new run in `runs/<new-id>/`, leaving the original
run untouched. The new trace includes `replay_of` pointing to the
original.

## Bit-exact replay

```bash
infini replay runs/latest/ --step s2 --freeze-model-calls
```

Replays with cached model responses. Useful for reproducing a flaky
failure without model non-determinism getting in the way.

## Compare original vs. replay

```bash
infini diff runs/latest/ runs/<new-id>/
```

Shows what changed between the original run and the replay. Useful for
"what if we'd used a different model tier?" or "what if we'd changed
the prompt?"

## Common debugging scenarios

- **A step failed.** Replay to it, inspect the input state, decide
  whether the input was wrong (upstream bug) or the step was wrong
  (this step's logic).
- **A verifier rejected the output.** Replay to the failing step, mutate
  the parameters, resume. Did the new output pass verification?
- **The loop ran 5 iterations and shipped on iteration 5.** Replay from
  iteration 3 to see what would have happened if you'd stopped there.

See [Chapter 7 of the Handbook](../../docs/handbook/replay.md) for the
full replay discipline.
