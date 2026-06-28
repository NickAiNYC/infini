# Architecture

The full system diagram and how the pieces fit together.

```text
Loopfile (loop.yaml)
  ↓
INFINI Parser + Validator
  ↓
Engine Adapter   ←─── Hermes (governance)  ·  OpenClaw (execution)
  ↓
Runtime
  ↓
Trace + Verification + Replay   (in INFINI)
  ↓
Observatory   (3D trace visualization)
```

## The layers

| Layer | What | Where |
| --- | --- | --- |
| **Format** | Loopfile — declarative YAML | [`spec/`](../../spec/) |
| **Engine** | Reference implementation | [`cli/`](../../cli/) |
| **Adapters** | Hermes, OpenClaw, community | [`adapters/`](../../adapters/) |
| **SDK** | Build your own adapter | [`sdk/`](../../sdk/) |
| **Observatory** | 3D trace visualizer | [`observatory-ui/`](../../observatory-ui/) |
| **Registry** | Adapter index | [`registry/`](../../registry/) |
| **Marketplace** | Loop index | [`marketplace/`](../../marketplace/) |
| **Corpus** | Benchmark cases | [`tests/corpus/`](../../tests/corpus/) |
| **Conformance** | Certification tests | [`tests/conformance/`](../../tests/conformance/) |

## The data flow

1. You write a `Loopfile.yaml`
2. `infini validate` checks it against the schema
3. `infini run` executes it (mock or live)
4. The engine produces a `run.json` trace
5. `infini inspect` reads the trace in the terminal
6. `infini ui` renders the trace in the 3D Observatory
7. `infini replay` time-travels to any step
8. `infini diff` compares two traces or two Loopfiles
9. `infini certify` runs the conformance suite against an adapter

## Cross-links

- [Portability](portability.md) — why the format is engine-agnostic
- [Adapter Development](adapter-development.md) — build the adapter layer
- [Certification](certification.md) — verify the adapter conforms
- [Observability](observability.md) — the trace layer
- [Replay](replay.md) — the time-travel layer
