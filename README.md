<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
  <img alt="INFINI" src="assets/banner.png" width="100%">
</picture>

# `INFINI`

### Serverless Orchestration for Autonomous AI Agents

[![Conformance](https://img.shields.io/badge/conformance-8%2F8-brightgreen?style=flat-square)](tests/conformance/)
[![Tests](https://img.shields.io/badge/tests-20%20passing-brightgreen?style=flat-square)](cli/tests/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Spec](https://img.shields.io/badge/spec-v1.0-00C853?style=flat-square)](spec/loopfile-v1.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f?style=flat-square)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/NickAiNYC/infini?style=flat-square&color=orange)](https://github.com/NickAiNYC/infini)
[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NickAiNYC/infini?quickstart=1)

</div>

**What if your AI agents had infinite memory, zero infrastructure costs, and could collaborate like a SWAT team?**

INFINI is the orchestration layer that makes it happen. Spin up agents. Give them tasks. Watch them plan, execute, and review each other's work. All through a single CLI. All with zero external dependencies.

```
Docker      standardized containers.
OpenTelemetry standardized traces.
Terraform   standardized infrastructure.
INFINI      standardizes AI agent loops.
```

**One command to rule them all:**

```bash
pip install infini-cli && infini setup && infini run my-loop.yaml --plan
```

<img src="assets/demo.gif" alt="INFINI Demo" width="700">

[![INFINI Demo — Side-by-side portability proof](https://asciinema.org/a/1FdlBnDl5EkYeDu3.svg)](https://asciinema.org/a/1FdlBnDl5EkYeDu3)

### Works with

| Adapter | Status | Compatibility |
| --- | :---: | :---: |
| [Hermes](adapters/hermes/) | ✅ Certified | 70.8% |
| [OpenClaw](adapters/openclaw/) | ✅ Certified | 66.7% |
| [LangGraph](adapters/langgraph/) | ⏳ Help wanted | — |
| [CrewAI](adapters/crewai/) | ⏳ Help wanted | — |
| [Mastra](adapters/mastra/) | ⏳ Help wanted | — |
| [Goose](adapters/goose/) | ⏳ Help wanted | — |
| [OpenAI Agents SDK](adapters/codex/) | ⏳ Help wanted | — |

---

## Ecosystem Integration Status

| Integration | Status | What Works | What's Missing |
|-------------|--------|------------|----------------|
| **LangGraph Adapter** | ✅ Implemented | Full adapter, 5 tests, `--engine langgraph` CLI | Live mode (mock only), replay |
| **OpenClaw Skill Adapter** | 🚧 In Progress | 5-skill resolver, export to Loopfile, mock execution | Live API calls, marketplace integration |
| **Hermes Verify Adapter** | 🚧 In Progress | Condition parser, mock confidence scoring | `hermes judge` CLI integration, live curator |
| **Supervisor Loop** | ✅ Reference Example | Loopfile validates, real trace generated (2 iters, 18 checks) | Live execution (mock mode works) |
| **Anthropic 3-Agent Harness** | ✅ Implemented | 7-step Loopfile, premature-victory prevention | Live execution (mock mode works) |

## Integration Compatibility Matrix

| Integration | Parse | Resolve | Execute | Trace | Verify | Replay | Status |
|-------------|:-----:|:-------:|:-------:|:-----:|:------:|:------:|--------|
| **Reference Engine** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Stable |
| **LangGraph Adapter** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | Stable |
| **OpenClaw Skill Adapter** | ✅ | ⚠️ | ⚠️ | ⚠️ | N/A | ❌ | Experimental |
| **Hermes Verify Adapter** | ✅ | N/A | N/A | ✅ | ⚠️ | N/A | Experimental |
| **Supervisor Loop** | ✅ | N/A | ⚠️ | ✅ | ✅ | ⚠️ | Reference |

**Legend:** ✅ = Fully implemented and tested · ⚠️ = Partial · ❌ = Not yet · N/A = Not applicable

---

## Why INFINI?

| Problem | INFINI Solution |
|---------|-----------------|
| **Agents have amnesia** | Eternal memory with FTS5 retrieval — verbatim storage, no summarization |
| **Coordination costs $$$** | SQLite bus = $0 infrastructure, sub-100ms scheduling latency |
| **Plugins are a mess** | Anthropic Skills standard — `infini skill install <git-url>` and go |
| **Agents hallucinate** | 3-agent supervision (Planner → Worker → Inspector) via SQLite message bus |
| **Complex setup** | One CLI, auto-installs `/infini` slash commands for Claude/Gemini/Codex |
| **Vendor lock-in** | Write a Loopfile once, run on any engine — same YAML, any framework |

<div align="center">

### Spaghetti → Spec

<img src="assets/spaghetti-to-spec.png" alt="150 lines of tangled framework code becomes 15 lines of declarative Loopfile YAML" width="800">

<sub>Stop hardcoding your agent logic into frameworks. Write it once as a standard spec, run it anywhere.</sub>

</div>

---

## 🎬 See It In Action

<img src="assets/demo.gif" alt="INFINI Demo — setup, task creation, 3-agent orchestration" width="700">

**What you're watching:**
1. `infini setup` → Initializes SQLite DB, detects AI terminals, installs slash commands
2. `infini validate loop.yaml` → Checks against the spec
3. `infini run loop.yaml --mock` → Executes deterministically (no API key)
4. `infini replay runs/latest/ --step s2` → Time-travel debug from any step
5. `infini certify adapters/hermes --mock` → Adapter certification (70.8%)
6. `infini engines` → The adapter ecosystem

---

## 🏗️ How It Works

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
- **`infini task *`** → Full task lifecycle (create/ack/complete/wait)
- **`infini skill install`** → Plug in any Anthropic Skills-compatible adapter
- **`infini run --live`** → Execute against real LLMs (Anthropic/OpenAI, no vendor lock-in)
- **`infini replay --step s2`** → Time-travel debug from any node

### For DevOps
- **Zero infrastructure** → No Redis, no message queues, no microservices
- **SQLite WAL mode** → Handles 50+ concurrent agents on a t3.micro
- **Single binary deployment** → `pip install` and you're done

### For AI Engineers
- **Eternal memory** → Verbatim storage + FTS5 retrieval (MemPalace pattern)
- **MCP runtime** → Model Context Protocol tool definitions + live execution
- **Full observability** → Every run produces a signed `.trace` file
- **3D Observatory** → Next.js + React Three Fiber trace visualizer

### For End Users
- **`/infini` slash commands** → Works inside Claude Code, Gemini CLI, Codex
- **One-command setup** → `infini setup` detects and configures everything
- **Declarative Loopfiles** → YAML workflows, no code required

---

## 📊 INFINI vs. The World

| Feature | INFINI | LangGraph | CrewAI | AutoGen |
|---------|--------|-----------|--------|---------|
| Zero-infra orchestration | ✅ | ❌ | ❌ | ❌ |
| Eternal memory (FTS5) | ✅ | ❌ | ❌ | ✅ |
| Slash command auto-install | ✅ | ❌ | ❌ | ❌ |
| 3-agent supervision | ✅ | ✅ | ❌ | ✅ |
| SQLite message bus | ✅ | ❌ | ❌ | ❌ |
| Adapter certification | ✅ | ❌ | ❌ | ❌ |
| Anthropic Skills standard | ✅ | ❌ | ❌ | ❌ |
| Time-travel replay | ✅ | ❌ | ❌ | ❌ |

---

## 🚀 Quick Start

```bash
# 1. Install
pip install infini-cli

# 2. Setup (init DB + detect terminals + install slash commands)
infini setup

# 3. Run your first workflow (mock mode — no API keys needed)
infini run examples/golden-research-assistant/research-loop.yaml --mock

# 4. Run with real agents (3-agent supervision)
infini run examples/golden-research-assistant/research-loop.yaml --plan

# 5. Run against a live LLM (needs ANTHROPIC_API_KEY or OPENAI_API_KEY)
infini run examples/golden-research-assistant/research-loop.yaml --live

# 6. Inspect the trace
infini inspect runs/latest/

# 7. Time-travel replay from any step
infini replay runs/latest/ --step s2

# 8. See your tasks
infini task list --status all

# 9. Install a community skill
infini skill install https://github.com/awesome/skill-repo

# 10. Certify an adapter
infini certify adapters/hermes --mock
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

memory:
  persist: true
  context_window: 100
```

---

## The Loopfile

A declarative `loop.yaml` that defines *what* your agent should do — not *how* one specific framework does it. Same file. Any engine. Full traceability.

📖 **[Read the spec →](spec/loopfile-v1.md)** · **[10 RFCs →](spec/rfcs/)** · **[Versioning policy →](spec/versions.md)**

### Native MCP Support

```yaml
TOOLS:
  - mcp: "github.com/modelcontextprotocol/servers/src/postgres"
  - mcp: "github.com/modelcontextprotocol/servers/src/github"
```

Drop in any MCP server with one line of YAML. No custom integrations.

---

## The Observatory

Every run produces a standardized trace. The Observatory is a local Next.js + React Three Fiber dashboard:

<div align="center">
  <img src="assets/observatory-ui.png" alt="INFINI Observatory — 3D execution graph" width="700">
</div>

- **3D Execution Graph** — Rotate, zoom, click any node for cost/tokens/artifacts
- **Time-Travel Debugging** — Replay from any node
- **Diff Analysis** — Compare runs side-by-side

---

## Certification

```bash
infini certify adapters/hermes --mock   # → certified (70.8%)
infini certify adapters/openclaw --mock  # → certified (66.7%)
```

📖 **[Certification reports →](registry/certifications/)** · **[Compatibility matrix →](spec/compatibility.md)**

---

## Canonical Corpus

INFINI's "ImageNet for agent loops" — 10 durable benchmark cases every engine should run.

| # | Case | Category |
| --- | --- | --- |
| 001 | simple-task | minimal, baseline |
| 002 | research-summary | research, verification |
| 003 | code-review | coding, parallel |
| 004 | retry-recovery | resilience |
| 005 | budget-guard | budget, safety |
| 006 | parallel-fanout | parallel, dag |
| 007 | memory-update | memory, learning |
| 008 | tool-call-placeholder | tools, mcp |
| 009 | human-approval-gate | governance |
| 010 | replay-diff | replay, diff |

📖 **[Full corpus →](tests/corpus/)**

---

## CLI Reference

```bash
infini validate loop.yaml           # Check against spec
infini run loop.yaml --mock         # Execute (no API key)
infini run loop.yaml --live         # Execute against real LLM
infini run loop.yaml --plan         # 3-agent orchestration
infini inspect runs/latest/         # Trace in terminal
infini replay runs/latest/ --step s2  # Time-travel debug
infini diff v1.yaml v2.yaml         # Semantic diff
infini ui runs/latest/run.json      # Launch Observatory
infini task create/ack/complete/list/wait  # Task lifecycle
infini skill list/install           # Skill management
infini certify adapters/<name>      # Adapter certification
infini conformance tests/conformance/  # Run conformance suite
infini engines                      # List adapters + skills
infini setup                        # Initialize everything
```

---

## 🤝 Join the Project

INFINI is open source. We synthesized proven patterns from Squad, MemPalace, Anthropic Skills, Superpowers, and FastMCP. Now we're building something bigger.

**Ways to contribute:**
- **Adapters** → Help us build for LangGraph, CrewAI, Mastra, Goose, Codex
- **Docs** → Write the [Loop Engineer Handbook](docs/handbook/)
- **Skills** → Create reusable skill repositories
- **Benchmarks** → Run performance tests against other frameworks
- **Corpus** → Add canonical benchmark cases

**Start here:**
```bash
git clone https://github.com/NickAiNYC/infini
cd infini
pip install -e './cli[dev]'
infini setup
infini conformance tests/conformance/ --mock
```

📖 **[Contributing Guide →](CONTRIBUTING.md)** · **[Adapter SDK →](sdk/)** · **[Architecture Decision Records →](docs/adr/)**

---

## 📖 The Story

INFINI synthesizes proven architectural patterns from 5 groundbreaking open-source projects:

- **[Squad](https://github.com/mco-org/squad)** → SQLite task/message bus and slash-command installer
- **[MemPalace](https://github.com/mempalace/mempalace)** → Verbatim storage with FTS5 retrieval
- **[Anthropic Skills](https://github.com/anthropics/skills)** → Plugin standard and skill marketplace
- **[Superpowers](https://github.com/obra/superpowers)** → 3-agent supervision pattern (Planner/Worker/Inspector)
- **[FastMCP](https://github.com/jlowin/fastmcp)** → Decorator-based tool definitions for live LLM execution

**We credit them. We love them. We stand on their shoulders.**

Read the full story: **[Scaling INFINI: How we built a serverless agent orchestration layer using SQLite](docs/blog/scaling-infini.md)**

---

## The Lineage

```
Docker      standardized   containers
Terraform   standardized   infrastructure
OpenAPI     standardized   APIs
Markdown    standardized   documents
INFINI      standardizes   autonomous work
```

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

<sub>Loops that don't end. Loops that improve.</sub>

</div>
