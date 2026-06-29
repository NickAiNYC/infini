<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
  <img alt="INFINI" src="assets/banner.png" width="100%">
</picture>

# `INFINI`

### The OpenTelemetry for Agent Loops

**Traces first. Portability second. Lock-in never.**

One spec. Any engine. Replayable traces.

[![Conformance](https://img.shields.io/badge/conformance-8%2F8-brightgreen?style=flat-square)](tests/conformance/)
[![Tests](https://img.shields.io/badge/tests-25%20passing-brightgreen?style=flat-square)](cli/tests/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/NickAiNYC/infini?style=flat-square&color=orange)](https://github.com/NickAiNYC/infini)

</div>

```bash
pip install infini-cli && infini run examples/hello-world.yaml --mock
```

[![INFINI Demo](https://asciinema.org/a/f0AuaBa237gzdT2K.svg)](https://asciinema.org/a/f0AuaBa237gzdT2K)

---

## The Portability Proof

**Same Loopfile. Two Engines. Identical Outcomes.**

```bash
infini run loops/canonical-supervisor/loop.yaml --mock --engine infini
infini run loops/canonical-supervisor/loop.yaml --mock --engine langgraph
infini diff runs/infini/run.json runs/langgraph/run.json
```

Result: both engines produce `verified` with the same trace format.

---

## Implementation Status

| Feature | Status | What Works |
|---------|--------|------------|
| **Loopfile Spec v1.0** | ✅ Stable | Full JSON Schema + EBNF grammar |
| **Mock Runtime** | ✅ Stable | `infini run --mock` — deterministic, no API keys |
| **Live LLM Execution** | ✅ Alpha | `infini run --live` — Anthropic/OpenAI via MCP |
| **LangGraph Adapter** | ✅ Stable | `--engine langgraph` with 5 tests, identical traces |
| **Time-Travel Replay** | ✅ Stable | `infini replay --step s2` — step-level debugging |
| **Trace Diff** | ✅ Stable | `infini diff` — compare runs across engines |
| **CrewAI Adapter** | ⏳ Help Wanted | Adapter SDK ready, bounty open |
| **Observatory UI** | 🚧 Preview | Local Next.js + React Three Fiber dashboard |
| **Registry** | 🚧 Preview | Certifications published, `infini install` planned |
| **Benchmarks** | 📋 Planning | 10-case corpus defined, suite not automated |
| **Production Runtime** | ❌ Not Yet | Do not use in production |

---

## What INFINI Actually Is

A **specification** for agent loops, with:
- A declarative YAML format (Loopfile)
- A conformance suite (proves it works)
- A trace schema (proves what happened)
- Adapters (proves it runs anywhere)

The 3-agent demo below is just one example. Loopfiles run on LangGraph too.

Like OpenTelemetry standardized observability across vendors, INFINI standardizes agent loop definitions across frameworks — with a trace schema you can export to any backend.

---

## Adapter Compatibility Matrix

| Adapter | Parse | Execute | Trace | Verify | Replay | Status |
|---------|:-----:|:-------:|:-----:|:------:|:------:|--------|
| **Reference Engine** | ✅ | ✅ | ✅ | ✅ | ✅ | Stable |
| **LangGraph** | ✅ | ✅ | ✅ | ✅ | ⚠️ | Stable |
| **Hermes** | ✅ | ⚠️ | ✅ | ⚠️ | ❌ | Beta |
| **OpenClaw** | ✅ | ⚠️ | ⚠️ | ❌ | ❌ | Experimental |
| **CrewAI** | 📋 | 📋 | 📋 | 📋 | 📋 | Help Wanted |

**Legend:** ✅ = Working · ⚠️ = Partial · ❌ = Not yet · 📋 = Planned

---

## The INFINI Difference

1. **Portability** — Same Loopfile runs on LangGraph, the reference engine, or any conformant adapter.
2. **Verifiability** — Built-in conformance suite proves it works. Semantic + syntactic checks.
3. **Replayability** — Every run leaves a trace. Debug from any step. Diff across engines.

---

## 🎬 See It In Action

[![INFINI Demo](https://asciinema.org/a/f0AuaBa237gzdT2K.svg)](https://asciinema.org/a/f0AuaBa237gzdT2K)

**What you're watching:**
1. `infini validate loop.yaml` → Checks against the spec
2. `infini run loop.yaml --mock` → Executes deterministically (no API key)
3. `infini inspect runs/latest/` → Trace in terminal
4. `infini replay runs/latest/ --step s2` → Time-travel debug
5. `infini certify adapters/hermes --mock` → Adapter certification
6. `infini engines` → The adapter ecosystem

---

## 🏗️ How It Works

*This is the INFINI reference engine — one way to run a Loopfile. The same Loopfile also runs on LangGraph, CrewAI, and others via adapters.*

```text
┌─────────────────────────────────────────────────────┐
│                     USER                            │
│               infini run --plan                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  PLANNER (Agent 1)                  │
│        Writes plan.md with step checklist           │
└─────────────────┬───────────────────────────────────┘
                  │ (SQLite Message Bus)
                  ▼
┌─────────────────────────────────────────────────────┐
│                  WORKER (Agent 2)                   │
│      Executes steps, updates tasks table            │
└─────────────────┬───────────────────────────────────┘
                  │ (SQLite Message Bus)
                  ▼
┌─────────────────────────────────────────────────────┐
│                 INSPECTOR (Agent 3)                 │
│         Reviews output, writes review.md            │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  ETERNAL MEMORY                     │
│         (SQLite FTS5 — verbatim retrieval)          │
└─────────────────────────────────────────────────────┘
```

**All without Redis. All without Kafka. Just SQLite.**

---

## ✨ Features

### For Developers
- **`infini run --plan`** → 3-agent supervision reduces hallucinations
- **`infini run --engine langgraph`** → Run on LangGraph (portability proof)
- **`infini task *`** → Full task lifecycle (create/ack/complete/wait)
- **`infini skill install`** → Plug in any Anthropic Skills-compatible adapter
- **`infini run --live`** → Execute against real LLMs (Anthropic/OpenAI)
- **`infini replay --step s2`** → Time-travel debug from any node

### For DevOps
- **Zero infrastructure** → No Redis, no message queues, no microservices
- **SQLite WAL mode** → Handles 50+ concurrent agents on a t3.micro
- **Single binary deployment** → `pip install` and you're done

### For AI Engineers
- **Eternal memory** → Verbatim storage + FTS5 retrieval
- **MCP runtime** → Model Context Protocol tool definitions + live execution
- **Full observability** → Every run produces a signed `.trace` file
- **3D Observatory** → Next.js + React Three Fiber trace visualizer

---

## 🚀 Quick Start

```bash
# 1. Install
pip install infini-cli

# 2. Run a Loopfile in mock mode (no API key needed)
infini run examples/golden-research-assistant/research-loop.yaml --mock

# 3. Run on LangGraph (portability proof)
infini run examples/hello-world.yaml --mock --engine langgraph

# 4. Inspect the trace
infini inspect runs/latest/

# 5. Time-travel replay from any step
infini replay runs/latest/ --step s2

# 6. Install the Anthropic 3-agent harness
infini registry install @anthropic/3-agent-harness
```

### Example Loopfile

```yaml
LOOPFILE: "1.0"
name: auth-module

OBJECTIVE: "Implement JWT auth with refresh tokens."

AGENTS:
  - { name: coder, role: builder, model_tier: sonnet, tools: [terminal.run, file_system.write] }
  - { name: judge, role: verifier, model_tier: haiku }

STEPS:
  - { id: s1, name: implement, action: terminal.run, uses: coder, produces: [auth.py] }
  - { id: s2, name: test, action: terminal.run, uses: coder, depends_on: [s1] }
  - { id: s3, name: verify, action: verify, uses: judge, depends_on: [s2] }

VERIFY:
  syntactic: ["auth.py:exists", "test-output.log:exit_zero"]
  semantic: ["judge:code_quality>=85"]
  confidence_threshold: 85

BUDGET: { dollars: 5, minutes: 15 }
STOP_WHEN: ["all_verify_passed"]
```

---

## The Loopfile

A declarative `loop.yaml` that defines *what* your agent should do — not *how* one specific framework does it. Same file. Any engine. Full traceability.

📖 **[Read the spec →](spec/loopfile-v1.md)** · **[11 RFCs →](spec/rfcs/)** · **[Versioning policy →](spec/versions.md)**

### Native MCP Support

```yaml
TOOLS:
  - mcp: "github.com/modelcontextprotocol/servers/src/postgres"
  - mcp: "github.com/modelcontextprotocol/servers/src/github"
```

---

## The Observatory

Every run produces a standardized trace. The Observatory is a local Next.js + React Three Fiber dashboard:

<div align="center">
  <img src="assets/observatory-ui.png" alt="INFINI Observatory — 3D execution graph" width="700">
</div>

---

## Certification

```bash
infini certify adapters/hermes --mock   # → certified (70.8%)
infini certify adapters/openclaw --mock  # → certified (66.7%)
```

📖 **[Certification reports →](registry/certifications/)** · **[Bounties →](bounties/)**

---

## CLI Reference

```bash
infini validate loop.yaml           # Check against spec
infini run loop.yaml --mock         # Execute (no API key)
infini run loop.yaml --live         # Execute against real LLM
infini run loop.yaml --engine langgraph  # Run on LangGraph
infini run loop.yaml --plan         # 3-agent orchestration
infini inspect runs/latest/         # Trace in terminal
infini replay runs/latest/ --step s2  # Time-travel debug
infini diff v1.json v2.json         # Compare traces
infini registry install @infini/hello-world  # Install from registry
infini task create/ack/complete/list/wait  # Task lifecycle
infini certify adapters/<name>      # Adapter certification
infini conformance tests/conformance/  # Run conformance suite
infini setup                        # Initialize everything
```

---

## 🤝 Join the Project

**Ways to contribute:**
- **Adapters** → Help us build for CrewAI, AutoGen, Mastra (bounties open)
- **Docs** → Write the [Loop Engineer Handbook](docs/handbook/)
- **Skills** → Create reusable skill repositories
- **Benchmarks** → Run performance tests against other frameworks

**Start here:**
```bash
git clone https://github.com/NickAiNYC/infini
cd infini
pip install -e './cli[dev]'
infini setup
infini conformance tests/conformance/ --mock
```

📖 **[Contributing Guide →](CONTRIBUTING.md)** · **[Adapter SDK →](sdk/)** · **[Bounties →](bounties/)** · **[ADRs →](docs/adr/)**

---

## 📖 The Story

INFINI synthesizes proven patterns from 5 open-source projects:

- **[Squad](https://github.com/mco-org/squad)** → SQLite task/message bus
- **[MemPalace](https://github.com/mempalace/mempalace)** → Verbatim storage with FTS5
- **[Anthropic Skills](https://github.com/anthropics/skills)** → Plugin standard
- **[Superpowers](https://github.com/obra/superpowers)** → 3-agent supervision pattern
- **[FastMCP](https://github.com/jlowin/fastmcp)** → Decorator-based tool definitions

Read the full story: **[Scaling INFINI](docs/blog/scaling-infini.md)**

---

## Community

- [Discussions](https://github.com/NickAiNYC/infini/discussions) — Questions, ideas, show & tell
- [RFCs](spec/rfcs/) — Propose spec changes
- [Contributing](CONTRIBUTING.md) — How to get involved
- [Code of Conduct](CODE_OF_CONDUCT.md) — Contributor Covenant 2.1

---

<div align="center">

**Star this repo if you want agents to be portable and inspectable.**

Built for the agent ecosystem. Spec is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). Code is [MIT](LICENSE).

<sub>Write once. Run anywhere. Debug everywhere.</sub>

</div>
