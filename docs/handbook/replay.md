# Replay

Chapter 7 of the [INFINI Handbook](README.md).

> Replay is what makes loops debuggable. Instead of `print` debugging an
> agent, you time-travel to the failing step, inspect state, change
> inputs, and re-run from there.

---

## Why replay

Agent runs fail. When they fail, the question is always: *what was the
state at step N?* Without replay, the answer is "rerun the whole thing
and hope it fails the same way." With replay, the answer is `infini
replay runs/latest/ --step N`.

Replay is the single biggest productivity win in Loop Engineering. It
turns debugging from a guessing game into a science.

---

## How replay works

When a loop runs, the engine persists state per step:

```yaml
STATE: { path: state/coding-loop/, resume: true }
```

For each step, the engine saves:

- The step's input state (the outputs of all `depends_on` steps).
- The step's parameters (resolved action, agent, tools).
- The step's output state (the artifacts it produced).
- A hash of the agent's prompt and the model's response.

When you replay:

```bash
infini replay runs/latest/ --step s3
```

The engine:

1. Loads the trace and state from `runs/latest/`.
2. Restores state to just before step `s3`.
3. Opens an interactive session where you can inspect state, change
   inputs, and resume.
4. On resume, executes from `s3` forward. Each subsequent step produces
   new artifacts in a new `runs/<new-id>/` directory, leaving the
   original run untouched.
5. Emits a new trace that includes a `replay_of` field pointing to the
   original run.

---

## What to use replay for

### 1. Debugging a failed step

A step failed. Why? Replay to it. Inspect the input state. Was the input
correct? If yes, the step's logic is wrong. If no, the upstream step is
wrong. Replay lets you bisect.

### 2. Testing "what if"

What if we'd used `model_tier: opus` instead of `sonnet` for the verify
step? Replay to that step, mutate the parameter, resume. You get a new
trace; compare it to the original with `infini diff`.

### 3. Reproducing a flaky failure

A loop failed once, then passed on retry. Why? Replay the failed run with
`--freeze-model-calls` to bit-exactly reproduce the original model
responses. Now you can debug without the model non-determinism getting in
the way.

### 4. Comparing engine behavior

Run a Loopfile on Hermes. Run the same Loopfile on OpenClaw. Replay the
Hermes trace on OpenClaw (cross-engine replay, planned for v1.1). The
diff tells you exactly where the engines diverge.

---

## Replay vs. rerun

Replay is not rerun. Rerun starts from scratch; replay resumes from a
point.

| | Rerun | Replay |
| --- | --- | --- |
| Cost | Full budget | Only the replayed steps' cost |
| Non-determinism | Re-invokes the model | By default, re-invokes; with `--freeze-model-calls`, bit-exact |
| State | Fresh | Restored from the original run |
| Output | New run in a new directory | New run, with `replay_of` pointing to original |
| Use case | "Run this again" | "What if I'd done X differently at step N?" |

---

## Cross-engine replay

A trace produced by engine A can be replayed on engine B if both engines
implement the `Replay` conformance capability. The trace format is
normative; the state format is engine-specific but must round-trip
through the trace.

This is the hardest part of the spec. It's the subject of v1.1 work. The
goal: a Hermes trace can be replayed on OpenClaw, and vice versa. This
makes the "engine swap" use case real — you can validate that a loop
behaves the same on a new engine before you commit to the swap.

---

## Replay failure modes

### 1. Non-deterministic models

The model gives a different answer on replay than on the original run.
This is expected; models are non-deterministic. Use
`--freeze-model-calls` to bit-exactly reproduce the original responses.

### 2. State that doesn't round-trip

The engine's state format doesn't survive serialization. This is an
engine bug; file an issue.

### 3. Side effects that can't be replayed

The original run wrote to a database; the replay can't write to the same
database (the row already exists). This is a real problem. The defense:
loops should declare their side effects in `ENGINE.tools`, and the
adapter should provide a "dry-run" mode that simulates side effects.

---

## What's next

- Chapter 8, [Governance](governance.md) — loops you can trust.
- For the full replay design, see [RFC-0003](../../spec/rfcs/RFC-0003-replay.md).
- For the replay CLI, see [`cli/README.md`](../../cli/README.md).
