# RFC-0003: Replay and Time-Travel

- Start date: 2026-06-28
- Status: draft
- Spec version: 1.0 (capability), 1.1 (rich replay)
- PR: TBD
- Implementation: `infini replay` ships in 1.0; full time-travel UI in 1.1

## Summary

Defines how a loop's execution can be replayed from any step. Replay is
what makes loops debuggable: instead of `print` debugging an agent, you
time-travel to the failing step, inspect state, change inputs, and re-run
from there.

## Motivation

Agent runs fail. When they fail, the question is always: *what was the
state at step N?* Without replay, the answer is "rerun the whole thing and
hope it fails the same way." With replay, the answer is `infini replay
runs/latest/ --step N`.

Replay must be:

- **Step-addressable.** You can resume from any step, not just the start.
- **State-faithful.** The state at step N is exactly what it was during the
  original run, not a re-approximation.
- **Mutable.** You can change inputs at the replay point to test "what if."
- **Traceable.** A replay produces its own trace, diffable against the
  original.

## Detailed design

### State persistence

The `STATE` block declares where state is persisted:

```yaml
STATE: { path: state/<loop-name>/, resume: true }
```

For each step, the engine persists:

- The step's input state (the outputs of all `depends_on` steps).
- The step's parameters (resolved action, agent, tools).
- The step's output state (the artifacts it produced).
- A hash of the agent's prompt and the model's response.

State is persisted before and after each step. This is what makes
step-addressable replay possible.

### Replay command

```bash
infini replay runs/latest/ --step s3
```

This:

1. Loads the trace and state from `runs/latest/`.
2. Restores state to just before step `s3`.
3. Opens an interactive session where the user can inspect state, change
   inputs, and resume.
4. On resume, executes from `s3` forward. Each subsequent step produces
   new artifacts in a new `runs/<new-id>/` directory, leaving the original
   run untouched.
5. Emits a new trace that includes a `replay_of` field pointing to the
   original run.

### Replay trace shape

```json
{
  "loopfile": "infini/coding-loop@1.0",
  "replay_of": "runs/2026-06-28-1042-coding/",
  "replay_from_step": "s3",
  "input_mutations": [
    { "step": "s3", "field": "params.command", "from": "pytest -q", "to": "pytest -q tests/auth/" }
  ],
  "started_at": "2026-06-28T11:02:00Z",
  "steps": [...],
  "outcome": "verified",
  "diff_vs_original": {
    "steps_changed": ["s3", "s4"],
    "cost_delta_usd": -0.42,
    "outcome_changed": false
  }
}
```

### Cross-engine replay

A trace produced by engine A can be replayed on engine B if both engines
implement the `Replay` conformance capability. The trace format is
normative; the state format is engine-specific but must round-trip through
the trace.

This is the hardest part of the spec. It is the subject of the v1.1 work.

## Alternatives considered

- **Re-run from scratch.** Rejected — non-deterministic models mean
  re-running rarely fails the same way.
- **Screenshot-based debugging.** Rejected — doesn't allow mutation.
- **Replay only at loop boundaries (not step boundaries).** Rejected —
  the step is the unit of work; you need step-level granularity to debug.
- **Replay without state persistence (re-derive state from inputs).**
  Rejected — too slow for non-trivial loops, and the re-derivation may
  not match the original.

## Backwards compatibility

v1.0. No prior version. The `Replay` capability is part of v1.0; engines
that don't implement it are marked `❌` in the compatibility matrix for
that column.

## Conformance impact

The `Replay` conformance capability requires the engine to:

1. Persist `STATE` per step.
2. Restore state at any step.
3. Accept input mutations at the replay point.
4. Execute from the replay point forward.
5. Emit a new trace with `replay_of` and `replay_from_step`.

## Open questions

- What is the minimum state schema that supports cross-engine replay?
  Current proposal: state is a content-addressed bag of artifacts plus a
  structured `agent_state` map. Open for debate.
- How are non-deterministic model calls handled in replay? Current answer:
  by default, replay re-invokes the model. A `--freeze-model-calls` flag
  replays with cached model responses for bit-exact reproduction.

## Future possibilities

- v1.1: rich replay UI in the Observatory (timeline scrubber, mutation
  editor, side-by-side diff).
- v1.2: branch replay — fork a run at step N and try multiple mutations
  in parallel.
- v2.0: replay across engines (run a Hermes trace on OpenClaw).

## Acknowledgements

Time-travel debugging is borrowed from Redux DevTools, rr (reverse
debugger), and LangSmith's trace replay.
