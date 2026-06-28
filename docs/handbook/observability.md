# Observability

Chapter 6 of the [INFINI Handbook](README.md).

> Loops you can't see are loops you can't trust.

---

## Why observability

Agent runs are opaque by default. You can see the final output; you can't
see *how* the agent got there. This makes agent systems hard to debug,
hard to trust, and hard to improve.

The defense is observability: every run produces a structured trace that
you can inspect, replay, and diff. The trace is not an afterthought; it's
part of the spec. An engine that doesn't emit traces is not conformant.

---

## The trace

Every run produces a `run.json` trace. The minimum shape is defined in
[`spec/loopfile-v1.md`](../../spec/loopfile-v1.md) §10:

```json
{
  "loopfile": "infini/coding-loop@1.0",
  "started_at": "2026-06-28T10:42:50Z",
  "ended_at":   "2026-06-28T10:47:22Z",
  "iterations": 3,
  "steps": [
    { "id": "s1", "status": "ok", "tokens": 4120, "cost_usd": 0.18,
      "artifacts": ["greetings.json"] }
  ],
  "verifications": [
    { "check": "tests:pass",            "status": "pass" },
    { "check": "judge:correctness>=90", "status": "pass", "confidence": 92 }
  ],
  "budget":  { "spent_dollars": 1.84, "spent_minutes": 4.53 },
  "outcome": "verified",
  "lessons": ["Prefer explicit JSON schema before drafting."]
}
```

Engines that emit richer traces (Hermes governance events, OpenClaw tool
calls) get richer views in the Observatory; engines that emit only the
minimum get the minimum views.

---

## The Loop Observatory

The Observatory is the signature feature of INFINI. It's the DevTools for
autonomous systems. See [RFC-0008](../../spec/rfcs/RFC-0008-observatory.md)
for the full design.

The Observatory has eight views:

1. **Timeline** — swimlane of every step, colored by engine lane.
2. **Decision graph** — DAG of STEPS, with edges showing `depends_on`.
3. **Iteration diff** — what changed between iterations.
4. **Memory snapshots** — lessons recalled and appended.
5. **Cost** — waterfall of token and dollar cost by step.
6. **Verification** — every check, its status, confidence, and threshold.
7. **Artifacts** — every file the loop produced, organized by step.
8. **Replay** — the replay studio.

The current Observatory is at `assets/observatory.png` (a rendered
mockup). The full UI ships in v1.1.

---

## What to look for in a trace

When you `infini inspect runs/latest/`, look for:

### 1. The outcome

Is it `verified`? If not, why not? The `verifications` array tells you
which check failed and (for semantic checks) the confidence score.

### 2. The cost waterfall

Which step consumed the most tokens? Often one step (usually a `plan` or
`research` step) consumes 60% of the budget. If so, can it be split into
smaller steps? Can it use a cheaper model tier?

### 3. The retry history

Did any step retry? If so, why? The `retry_attempt` field tells you how
many times. A step that retried 3 times is a step that needs a better
prompt or a better tool, not a higher retry limit.

### 4. The artifact list

Did the loop produce what you expected? Each artifact should map to a
step's `produces` declaration. Missing artifacts are a sign of a step that
silently failed.

### 5. The lesson

What did the loop learn? If the lesson is generic ("be careful"), the
loop didn't actually learn. If it's specific ("start from `src/App.tsx`
because the toggle lives there"), the loop learned something useful.

---

## Traces are portable

A trace produced by engine A can be inspected by the Observatory running
on engine B's machine. The Observatory is a static web app that reads
`run.json` from disk or from a URL. There is no backend.

This means you can share traces. Paste a `run.json` into a GitHub
Discussion; anyone can open it in their Observatory and see what
happened. This is how the community debugs loops together.

---

## Traces are signed

Every trace is signed by the engine that produced it (per
[RFC-0009](../../spec/rfcs/RFC-0009-provenance.md)). The signature covers
the Loopfile hash, the engine identity, the timestamps, the outcome, and
the artifact hashes.

This means you can verify that a trace was produced by the engine it
claims to be from, and that it hasn't been tampered with since. Traces
are evidence, not just logs.

---

## What's next

- Chapter 7, [Replay](replay.md) — how to debug loops using the trace.
- For the full Observatory design, see [RFC-0008](../../spec/rfcs/RFC-0008-observatory.md).
- For the trace schema, see [`spec/loopfile-v1.md`](../../spec/loopfile-v1.md) §10.
