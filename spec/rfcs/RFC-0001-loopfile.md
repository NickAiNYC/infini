# RFC-0001: Loopfile v1.0

- Start date: 2026-06-28
- Status: implemented
- Spec version: 1.0
- PR: #1 (initial commit)
- Implementation: shipped in `infini 1.0.0`

## Summary

Defines the v1.0 Loopfile: a YAML document that declares an autonomous agent
loop's objective, agents, steps, verification, budget, and stop conditions.
Any conforming engine can parse, run, verify, inspect, replay, and diff a
v1.0 Loopfile.

## Motivation

Before v1.0, every agent framework (LangGraph, CrewAI, AutoGen, OpenClaw,
Hermes) reinvented the same primitives — state, resume, verification, cost
ceilings, self-improvement — with incompatible representations. A loop
written for one runtime was useless in another.

A portable format lets teams:

- Write a loop once and run it on any engine.
- Swap engines without rewriting loops.
- Inspect, replay, and diff loops across engines using one tool.

## Detailed design

The full v1.0 spec is in [`loopfile-v1.md`](../loopfile-v1.md). The
normative artifacts are:

- [`loopfile-v1.md`](../loopfile-v1.md) — the spec, normative.
- [`grammar.ebnf`](../grammar.ebnf) — formal grammar.
- [`schema.json`](../schema.json) — JSON Schema used by `infini validate`.

Top-level fields:

```yaml
LOOPFILE: "1.0"
name: <slug>
version: <semver>
description: <string>
OBJECTIVE: <string>
AGENTS: [...]
STEPS: [...]
VERIFY: { syntactic, semantic, confidence_threshold }
BUDGET: { dollars, minutes, tokens? }
STOP_WHEN: [...]
LESSONS: { path, append }?
STATE: { path, resume }?
```

The six conformance capabilities:

| Capability | Meaning |
| --- | --- |
| Parse Loopfile | Accept any v1.0 Loopfile; reject invalid ones per schema.json. |
| Run Loop | Execute the STEPS DAG with declared AGENTS. |
| Verify | Run syntactic and semantic checks; report confidence. |
| Inspect Trace | Emit a `run.json` trace per spec §10. |
| Replay | Resume from any step using saved STATE. |
| Diff | Produce a semantic diff between two Loopfile versions. |

## Alternatives considered

- **JSON instead of YAML.** Rejected — YAML is more human-readable for
  declarative files and supports comments. JSON Schema is still used for
  validation.
- **A graph format (DAG-only, no ordered-list option).** Rejected — ordered
  lists are more readable for simple loops; `depends_on` adds the DAG when
  needed.
- **Embedding the model name (`model: gpt-4o`).** Rejected — would make
  Loopfiles non-portable across model providers. `model_tier` is
  engine-resolved instead.
- **First-class composition (`CALLS:` block).** Deferred to RFC-0011+. v1.0
  supports composition through `depends_on` and step references; explicit
  sub-loop calls are a v1.1 candidate.

## Backwards compatibility

This is v1.0. There is no prior version to be compatible with. The
`LOOM:` → `LOOPFILE:` rename from the pre-1.0 era is covered in
[`migration.md`](../migration.md).

## Conformance impact

This RFC *defines* conformance. The six capabilities above are the
conformance contract. An adapter's conformance row in
[`compatibility.md`](../compatibility.md) tracks which capabilities it
implements.

## Open questions

- Should `model_tier` be a registry-defined enum or remain engine-resolved?
  Current answer: engine-resolved. Revisit at v1.1.
- How should loops compose? Tracked in a future RFC.
- What is the minimum trace schema that supports cross-engine replay?
  Addressed in [RFC-0003](RFC-0003-replay.md).

## Future possibilities

- v1.1: `PACKS:`, `METRICS:`, `HOOKS:`.
- v2.0: typed `OBJECTIVE`, composition as a primitive.

## Acknowledgements

The format draws on Dockerfile (declarative, portable, versioned),
Terraform (resource DAG), GitHub Actions (job dependencies), and the
SRE Book (verification as a discipline).
