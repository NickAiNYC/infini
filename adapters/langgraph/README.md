# INFINI × LangGraph Adapter

> **The proof of portability.** The same Loopfile runs on both the INFINI reference engine and LangGraph, producing equivalent traces.

## Status: Preview

- ✅ `parse_loopfile` — parses any v1.0 Loopfile
- ✅ `run_loop` — executes in mock mode (deterministic, no API key)
- ✅ `verify` — runs syntactic + semantic checks
- ✅ `inspect_trace` — produces INFINI-format `run.json`
- 🚧 `replay` — planned
- 🚧 `diff` — planned
- 🚧 Live mode (requires `langgraph` installed) — planned

## Install

```bash
pip install infini-cli[langgraph]
```

## Use

```bash
# Run a Loopfile on LangGraph (mock mode)
infini run loop.yaml --engine langgraph --mock

# Compare traces between engines
infini run loop.yaml --mock -o runs/reference/
infini run loop.yaml --engine langgraph --mock -o runs/langgraph/
infini diff runs/reference/run.json runs/langgraph/run.json
```

## How it works

```text
Loopfile (YAML)
  ↓
LangGraphAdapter.parse()
  ↓
LangGraphAdapter.to_state_graph()
  ├─ STEPS → LangGraph nodes
  ├─ depends_on → LangGraph edges
  ├─ VERIFY → conditional edges (pass → exit, fail → retry)
  └─ BUDGET → recursion limit + cost tracking
  ↓
LangGraphAdapter.run()
  ↓
INFINI Trace (run.json — same format as reference engine)
```

## Architecture

The adapter translates Loopfile primitives to LangGraph primitives:

| Loopfile | LangGraph |
|----------|-----------|
| `STEPS` | Nodes in a `StateGraph` |
| `depends_on` | Edges between nodes |
| `VERIFY` | Conditional edge after last node |
| `BUDGET` | Recursion limit + cost tracking |
| `STOP_WHEN` | Graph termination conditions |
| `AGENTS` | Node functions with model tier resolution |

## Tests

```bash
python -m pytest cli/tests/test_langgraph_adapter.py -q
```

5 tests covering: parsing, graph translation, mock execution, trace format compatibility, and budget enforcement.

## Attribution

Pattern adapted from LangGraph's StateGraph architecture.
