# INFINI × LangGraph Adapter

> **Status: Help Wanted.** This adapter is not yet implemented.
> This is a community adapter — see [Contributing](../../CONTRIBUTING.md)
> and the [Adapter SDK](../../sdk/) to get started.

## What this adapter does

LangGraph (https://github.com/langchain-ai/langgraph) is Graph-based agent orchestration from the LangChain team. Stateful, cyclic, controllable.

This adapter would let any Loopfile run as a langgraph workflow, with
full conformance to the INFINI spec: Parse, Run, Verify, Inspect, Replay.

## Why build this?

- **It's the easiest external contribution.** The Adapter SDK gives you
  the base class; you implement the six capabilities.
- **It proves the portability claim.** A Loopfile that runs on both
  Hermes and LangGraph is the demonstration that INFINI is real.
- **It grows the ecosystem.** Every new adapter in the matrix makes the
  standard more valuable to adopters.

## How to start

1. Read the [Adapter SDK README](../../sdk/README.md).
2. Read the [Adapter Interface Reference](../../sdk/adapter-interface.md).
3. Copy [`sdk/examples/minimal-adapter.md`](../../sdk/examples/minimal-adapter.md)
   as a starting point — it's a working PARSE-only adapter in ~50 lines.
4. Implement `RUN`, then `VERIFY`, then `INSPECT`, then `REPLAY`.
5. Run `infini conformance tests/conformance/ --engine=langgraph` to verify.
6. PR to this directory with your adapter + at least one example Loopfile.

## Conformance target

| Capability | Required |
| --- | :---: |
| Parse Loopfile | ✅ (minimum to be listed) |
| Run Loop | ✅ |
| Verify | ✅ |
| Inspect Trace | 🚧 (next) |
| Replay | 🚧 (later) |
| Diff | 🚧 (later) |

See [`spec/compatibility.md`](../../spec/compatibility.md) for the full
matrix and the conformance test suite.

## Files to create

```
adapters/langgraph/
├── README.md          ← this file (replace with real docs when implemented)
├── adapter.yaml       ← the adapter manifest (name, version, capabilities)
├── __init__.py        ← the adapter module
└── examples/
    └── langgraph-loop.yaml   ← at least one runnable example Loopfile
```

## Questions?

Open a Discussion at https://github.com/NickAiNYC/infini/discussions
with the `adapters` label.

---

**Help wanted.** If you build this, you become the maintainer of the
LangGraph adapter. Your name goes in CONTRIBUTORS.md.
