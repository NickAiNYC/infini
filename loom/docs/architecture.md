# Architecture

Loom is intentionally small. The goal is to ship a format, not a runtime.

```
┌────────────────────────────────────────────────────────────┐
│                      YOU WRITE                              │
│                                                             │
│   Loopfile    ←  one file, runtime-agnostic, portable       │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                     LOOM CLI                                │
│                                                             │
│   validate · inspect · replay · diff · ci                   │
│   run · install · publish · search · engines                │
└────────────────────────┬───────────────────────────────────┘
                         │
            ┌────────────┴───────────────┐
            ▼                            ▼
┌───────────────────────┐     ┌──────────────────────────────┐
│   ENGINE ADAPTERS     │     │       LOOM REGISTRY          │
│                       │     │                              │
│  langgraph            │     │  publish · install · search  │
│  crewai               │     │  signed · versioned · curated│
│  openclaw             │     │                              │
│  hermesagents         │     └──────────────────────────────┘
│  autogen              │
│  smolagents           │
│  (your engine here)   │
└───────────┬───────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│                  RUNTIME ARTIFACTS                          │
│                                                             │
│   runs/{ts}/trace.jsonl    ← every event, append-only       │
│   state/loop_state.json    ← resumable state                │
│   state/lessons.md         ← self-improvement log           │
└────────────────────────────────────────────────────────────┘
```

## Design principles

1. **Format over runtime.** We do not ship an engine. We ship the contract engines agree on.
2. **Append-only logs.** Traces are JSONL. Safe under crash. Greppable.
3. **Atomic state.** State writes use temp-file + rename. Torn writes cannot corrupt.
4. **Two-tier verification minimum.** Loops without ≥2 tiers are marked `UNVERIFIED`.
5. **Cheap by default.** Model routing is explicit. Haiku for routine, Sonnet for execution, Opus for judgment.
6. **Resume, don't restart.** State is the source of truth. Restarting from scratch is a bug.
7. **Self-improvement is mandatory.** Every run appends to `lessons.md`. A loop that does not improve is a script pretending to be a loop.

## Components

### `spec/`
The contracts. Loopfile, trace, state. These change slowly and only via RFC.

### `cli/`
The reference CLI. `validate`, `inspect`, `replay`, `diff`, `ci` ship working today. `run`, `install`, `publish` require adapters / registry.

### `loops/`
12 canonical loops. Each is a working Loopfile with a documented objective, inputs, verification, budget, and stop conditions.

### `prompts/`
The Loop Engineer prompt. Defines a role, not a tool.

### `registry/`
The RFC for the registry. Not live yet.

### `.github/workflows/`
The CI that runs `loom validate` + `loom ci` on every PR.

## What Loom is not

- Not a runtime. We do not execute agents.
- Not a model router. We specify tiers; engines pick models.
- Not a prompt library. We specify a format; prompts live in loops.
- Not a vendor lock-in. The spec is CC-BY-4.0. The CLI is MIT.

## Extension points

- **Engine adapters** — any runtime that can read YAML and emit JSONL can be Loom-compatible.
- **Verification primitives** — `syntactic`, `semantic`, `external` are categories; specific checks (`tests:pass`, `rubric:90`) are extensible.
- **State backends** — v1 is file-based. v1.1 may add SQLite, Redis.
- **Registry namespaces** — `loom/*`, `<org>/*`, `<user>/*`. Anyone can publish to their namespace.
