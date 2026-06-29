<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
  <img alt="INFINI" src="assets/banner.png" width="100%">
</picture>

# INFINI — Portable Agent Loop Spec

**Experimental.** Define a workflow once as a Loopfile. Run it on three engines.
Compare the traces. They match.

[![Tests](https://img.shields.io/badge/tests-25%20passing-brightgreen?style=flat-square)](cli/tests/)
[![Conformance](https://img.shields.io/badge/conformance-8%2F8-brightgreen?style=flat-square)](tests/conformance/)
[![Portability](https://img.shields.io/badge/portability-3%20engines-blue?style=flat-square)](proof/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

**Status: early alpha.** Reference, LangGraph, and Local engines working.
Other adapters planned. Do not use in production.

---

## Three engines. One Loopfile. Identical traces.

```bash
infini run loop.yaml --engine infini --trace ref.json    # Reference engine
infini run loop.yaml --engine langgraph --trace lg.json   # LangGraph
infini run loop.yaml --engine local --trace local.json    # Local LLM (Qwythos)

infini diff ref.json local.json   # → Identical structure
infini diff lg.json local.json    # → Identical structure
```

| Engine | Mock Mode | Live Mode | Open-Weight | Offline | Cost |
|--------|-----------|-----------|-------------|---------|------|
| Reference | ✅ | ⚠️ (via MCP) | ❌ | ✅ | $0 |
| LangGraph | ✅ | ✅ | ❌ | ❌ | $ |
| **Local (Qwythos)** | ❌ | ✅ | ✅ | **✅** | **$0** |

The **Local engine** runs a real LLM (Qwythos-9B GGUF) on consumer hardware.
No API key. No internet. Deterministic output at `--temp 0.0`.

---

## Why

Today, moving an agent workflow between frameworks usually means rewriting
orchestration logic. INFINI separates the workflow specification from the
runtime so the same Loopfile can execute across supported engines while
producing comparable execution traces.

---

## 60-second install

```bash
pip install infini-cli
```
(Currently install from source while the package stabilizes.)

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
pip install -e './cli[dev]'
infini conformance tests/conformance/ --mock
```

---

## One Loopfile

```yaml
LOOPFILE: "1.0"
name: hello-world
OBJECTIVE: "Demonstrate portability across engines."
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS:
  - { id: s1, name: greet, action: write.greeting, uses: builder, produces: [greeting.txt] }
VERIFY:
  syntactic: ["greeting.txt:exists"]
  semantic: []
  confidence_threshold: 80
BUDGET: { dollars: 1, minutes: 5 }
STOP_WHEN: ["all_verify_passed"]
```

Full spec: [loopfile-v1.md](spec/loopfile-v1.md)

---

## Run on all three engines

```bash
# Reference engine (mock)
infini run examples/hello-world/Loopfile.yaml --mock

# LangGraph engine (mock or live)
infini run examples/hello-world/Loopfile.yaml --mock --engine langgraph

# Local engine (fully offline, real LLM)
infini setup --download-qwythos           # Download the model (~5.6GB)
infini run loop.yaml --engine local --live
```

## Diff the traces

```bash
infini run loop.yaml --mock -o runs/reference
infini run loop.yaml --mock --engine langgraph -o runs/langgraph
infini run loop.yaml --engine local --trace runs/local

infini diff runs/reference/run.json runs/langgraph/run.json
infini diff runs/langgraph/run.json runs/local/run.json
```

All three engines produce `verified` with the same trace schema.

Full proof: [proof/](proof/) — run the reproducible portability proof yourself.

---

## Feature matrix

| Feature | Status |
|---------|--------|
| Loopfile spec v1.0 | Stable — full JSON Schema + EBNF grammar |
| `infini run --mock` | Deterministic, no API keys needed |
| `infini run --engine langgraph --mock` | LangGraph runtime, identical traces |
| `infini run --engine local --live` | **NEW** — Real LLM, fully offline, $0 cost |
| `infini setup --download-qwythos` | **NEW** — One-command local model download |
| `infini audit .` | Scans project for 12 loop-readiness signals, returns 0-100 score |
| `infini init --pattern daily-triage` | Scaffolds 5 canonical patterns |
| `infini run --work-dir` | Real filesystem verification |
| `infini replay --step s2` | Time-travel debug from any step |
| `infini diff` | Compare traces across engines |
| `infini validate` | Validates Loopfiles against schema |
| 25 unit tests + 8 conformance tests | All passing |

## What's NOT ready

- 4 of 6 adapters (CrewAI, AutoGen, Mastra, OpenAI Agents). CLI accepts
  `--engine crewai` but the runtime isn't wired — it will error.
- Production use. Zero users. The repo is public for feedback, not deployment.
- Observatory UI exists as a prototype. It currently renders mock data until
  live trace ingestion is implemented.

## How to contribute

- **Adapters** — Help wire CrewAI, AutoGen, Mastra. Adapter manifests exist;
  the runtime just needs building.
- **Live mode testing** — Run the same Loopfile on two engines in live mode
  and post the trace diff.
- **Feedback** — Run `infini audit .` on your project and open an issue telling
  me if the signals feel wrong.

[Contributing Guide](CONTRIBUTING.md) · [Adapter SDK](sdk/) ·
[Discussions](https://github.com/NickAiNYC/infini/discussions) ·
[License: MIT](LICENSE)

---

*MIT licensed reference implementation of the INFINI Loopfile specification.
Spec is CC-BY-4.0. Code is MIT.*
