# Loopfile Specification — Version 1.0

Status: **Draft** (open for community feedback)
Last updated: 2026-06-28
Stability: `LOOPFILE: "1.0"` is the normative version string.

> **INFINI runs Loopfiles.** This document defines what a Loopfile is.

A Loopfile is a portable, declarative description of an autonomous agent loop. Any conforming engine can parse it, execute it, verify its outputs, and produce a trace that any other conforming engine can inspect, replay, or diff.

---

## 1. Goals

1. **Portability** — a Loopfile written for one engine runs on any other.
2. **Inspectability** — every execution produces a structured, replayable trace.
3. **Verifiability** — every loop declares what counts as "done" and how to check it.
4. **Bounded cost** — every loop declares a budget that the engine must enforce.
5. **Composability** — loops can depend on, call, and produce other loops.

## 2. Non-goals

- Defining how agents reason. Engines decide that.
- Defining model APIs. Loopfiles declare `model_tier` only.
- Replacing workflows. Loops are autonomous; workflows are scripted. Both belong.

## 3. File format

A Loopfile is a YAML 1.2 document with the top-level key `LOOPFILE: "1.0"`.

```yaml
LOOPFILE: "1.0"
name: <string>
version: <semver>
description: <string>            # optional
OBJECTIVE: <string>
AGENTS: [ <agent> ]
STEPS:  [ <step>  ]
VERIFY: { syntactic: [...], semantic: [...], confidence_threshold: <int> }
BUDGET: { dollars: <number>, minutes: <number> }
STOP_WHEN: [ <predicate> ]
```

See [`grammar.ebnf`](grammar.ebnf) for the formal grammar and [`schema.json`](schema.json) for the JSON Schema used by `infini validate`.

## 4. Top-level fields

| Field              | Type     | Required | Description |
| ------------------ | -------- | :------: | ----------- |
| `LOOPFILE`         | string   | yes      | Spec version. Must be `"1.0"`. |
| `name`             | string   | yes      | Slug, `[a-z0-9-]+`. Unique within a registry namespace. |
| `version`          | semver   | yes      | Loopfile version, independent of spec version. |
| `description`      | string   | no       | Human-readable summary. |
| `OBJECTIVE`        | string   | yes      | The single sentence the loop is trying to satisfy. |
| `AGENTS`           | list     | yes      | Named roles the loop can dispatch to. |
| `STEPS`            | list     | yes      | Ordered or DAG-ordered operations. |
| `VERIFY`           | map      | yes      | How the engine decides the loop is correct. |
| `BUDGET`           | map      | yes      | Hard ceiling on dollars and wall-clock minutes. |
| `STOP_WHEN`        | list     | yes      | Predicates that terminate the loop. |
| `LESSONS`          | map      | no       | Path to append lesson-learned entries after each run. |
| `STATE`            | map      | no       | Where to persist loop state for resume. |

## 5. AGENTS

```yaml
AGENTS:
  - name: builder
    role: builder
    model_tier: haiku        # haiku | sonnet | opus | gpt-4o | ...
    tools: [read, write, bash]
  - name: judge
    role: verifier
    model_tier: sonnet
    tools: [read]
```

- `name` is referenced by `STEPS[].uses`.
- `role` is one of: `builder`, `verifier`, `critic`, `researcher`, `planner`.
- `model_tier` is engine-resolved. The Loopfile does not pin a specific model.
- `tools` is engine-resolved. The Loopfile declares intent; the engine maps to real tools.

## 6. STEPS

```yaml
STEPS:
  - id: s1
    name: greet
    action: write_greetings
    uses: builder
    produces: [greetings.json]
  - id: s2
    name: verify
    action: judge_greetings
    uses: judge
    depends_on: [s1]
```

- `id` is unique within the Loopfile.
- `depends_on` forms a DAG. Cycles are allowed (that's what makes it a loop).
- `action` is engine-resolved. The Loopfile names the *intent*, not the implementation.
- `produces` declares artifacts the step emits. These are part of the trace.
- A step may declare `retry: { max: 3, backoff: exponential }`.

## 7. VERIFY

```yaml
VERIFY:
  syntactic: ["tests:pass", "lint", "greetings.json:valid_json"]
  semantic:  ["judge:correctness>=90", "rubric:accessibility>=85"]
  confidence_threshold: 85
```

- `syntactic` checks are deterministic (exit code, schema, linter).
- `semantic` checks are model-judged and produce a 0–100 confidence score.
- `confidence_threshold` is the minimum mean confidence across semantic checks for the loop to be considered *verified*.
- A loop that exits without all checks passing is **not** shipped, regardless of `STOP_WHEN`.

## 8. BUDGET

```yaml
BUDGET: { dollars: 5, minutes: 15, tokens: 500000 }
```

- `dollars` and `minutes` are required. `tokens` is optional.
- The engine must abort the loop and mark the run `budget_exceeded` if any ceiling is breached.
- Partial work is preserved in the trace for replay.

## 9. STOP_WHEN

```yaml
STOP_WHEN: ["all_verify_passed"]
```

Recognized predicates:

| Predicate | Meaning |
| --- | --- |
| `all_verify_passed` | Both syntactic and semantic checks pass, confidence ≥ threshold. |
| `budget_remaining<10%` | Stop when ≤10% of any budget remains. |
| `iterations>=N` | Stop after N iterations of the outer loop. |
| `confidence>=N` | Stop when semantic confidence ≥ N. |
| `predicate:<name>` | User-defined predicate, resolved by engine. |

A Loopfile must declare at least one stopping predicate.

## 10. Traces

Every conforming engine must produce a `run.json` trace containing, at minimum:

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
    { "check": "tests:pass",           "status": "pass" },
    { "check": "judge:correctness>=90","status": "pass", "confidence": 92 }
  ],
  "budget":  { "spent_dollars": 1.84, "spent_minutes": 4.53 },
  "outcome": "verified",
  "lessons": ["Prefer explicit JSON schema before drafting."]
}
```

This is what `infini inspect`, `infini replay`, and `infini diff` operate on.

## 11. Conformance

An engine is **Loopfile-conformant** if it can:

1. **Parse** any v1.0 Loopfile and reject invalid ones using [`schema.json`](schema.json).
2. **Run** the loop's STEPS DAG with declared AGENTS.
3. **Enforce** the BUDGET.
4. **Verify** against the VERIFY block and report confidence.
5. **Emit** a `run.json` trace matching §10.
6. **Resume** from any step using saved state.

Partial conformance (e.g., parse-only, run-without-replay) is allowed and tracked in [`compatibility.md`](compatibility.md).

## 12. Versioning

- `LOOPFILE: "1.0"` is fixed for any Loopfile conforming to this document.
- Minor revisions (1.1, 1.2) are additive and backward-compatible.
- Major revisions (2.0) require migration. See [`migration.md`](migration.md).

## 13. Open questions

- Should `model_tier` be a registry-defined enum or remain engine-resolved?
- How should loops compose? (RFC-0004 — Registry, will inform this.)
- What is the minimum trace schema that supports cross-engine replay?

Open an RFC in `spec/` to propose changes.
