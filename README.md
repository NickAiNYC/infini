<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.png">
  <img alt="INFINI" src="assets/logo.png" width="320">
</picture>

<br><br>

# `INFINI`

### The Open Standard for Agent Portability

Write your agent logic **once**. Execute it on **any** framework.<br>Verify it actually worked. Replay it when it didn't.

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/milestone-Reference_Runtime-blueviolet?style=flat-square)](#the-reference-runtime)
[![Spec](https://img.shields.io/badge/spec-v1.0-00C853?style=flat-square)](#the-loopfile)
[![Stars](https://img.shields.io/github/stars/NickAiNYC/infini?style=flat-square&color=orange)](https://github.com/NickAiNYC/infini)
[![Discord](https://img.shields.io/badge/Discord-join-5865F2?style=flat-square&logo=discord&logoColor=white)](#community)

<br>

> **Agents just got their Docker moment.**

[Install](#install) · [Quickstart](#quickstart) · [Observatory](#-the-observatory) · [Adapters](#-adapters) · [Manifesto](MANIFESTO.md) · [Spec](spec/loopfile-v1.md) · [Roadmap](ROADMAP.md)

<br>

<img src="assets/demo.gif" alt="INFINI Demo" width="700">

</div>

<br>

---

<br>

<div align="center">

```
                    ┌─────────────┐
                    │  Loopfile   │    ← Portable. Declarative. Yours.
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Engine    │    ← Reference, Hermes, OpenClaw, yours
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼───┐ ┌──────▼──────┐
        │  Adapter   │ │ Trace │ │  Verifier   │
        └─────┬─────┘ └───┬───┘ └──────┬──────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │ Observatory │    ← See everything. Replay anything.
                    └─────────────┘
```

</div>

<br>

## The Problem

Current agent frameworks create **massive vendor lock-in**. Your core logic gets entangled with LangChain, CrewAI, AutoGen, OpenAI Agents SDK — switching runtimes means rewriting everything. Traces are opaque. Verification is an afterthought. Migration debt compounds silently.

**INFINI is the escape hatch.**

<br>

## The Loopfile

A declarative `loop.yaml` that defines *what* your agent should do — not *how* one specific framework does it.

```yaml
LOOPFILE: "1.0"
name: research-assistant

AGENTS:
  - { name: researcher, model_tier: sonnet, tools: [browser] }
  - { name: verifier,  model_tier: haiku }

STEPS:
  - { id: s1, action: browser.find_sources, uses: researcher }
  - { id: s2, action: verify_citations, uses: verifier, depends_on: [s1] }

VERIFY:
  syntactic: ["every_claim_has_citation"]
  semantic: ["source_quality >= 85"]
  confidence_threshold: 85

BUDGET: { dollars: 6, minutes: 20 }
STOP_WHEN: ["all_verify_passed"]
```

Same file. Any engine. Full traceability.

<br>

## Quickstart

```bash
pip install infini-cli

# Run a loop end-to-end
infini run research-loop.yaml
```

```
✓ Loaded Loopfile
✓ Loaded adapter
✓ Executing...
✓ Verification passed
✓ Trace saved
✓ Observatory updated
```

```bash
# Or try mock mode (no API key needed)
infini run examples/golden-research-assistant/research-loop.yaml --mock

# Launch the Observatory
infini ui runs/latest/run.json
```

<br>

## The Reference Runtime

> **Current Milestone** — this is what we're building right now.

The next release is not a patch. It's a named milestone: **The Reference Runtime**.

<div align="center">

```
Loopfile → Engine → Adapter → Execution → Trace → Replay → Observatory
```

</div>

When that path works end-to-end, everything else becomes easy. One demo that shows a Loopfile executing for real, generating a trace, and lighting up the Observatory communicates the entire value of the project.

<details>
<summary><b>Milestone breakdown</b></summary>

<br>

| Milestone | What ships | Status |
|-----------|-----------|--------|
| **1 — Reference Runtime** | Execute Loopfiles for real. Generate structured traces. Support replay from traces. | `in-progress` |
| **2 — Adapter Ecosystem** | Stable adapter SDK. Hermes adapter. OpenClaw adapter. Community adapter examples. | `next` |
| **3 — Observatory** | Live execution timeline. Trace visualization. Verification reports. Cost/runtime metrics. | `next` |
| **4 — Registry** | Publish loops. Search loops. Version loops. Rate and review loops. | `planned` |

</details>

<br>

## The Observatory

Every run produces a standardized trace. The Observatory is a local Next.js + React Three Fiber dashboard:

<div align="center">
  <img src="assets/observatory-ui.png" alt="INFINI Observatory — 3D execution graph" width="700">
</div>

<br>

- Drop in a `.trace` file — interactive 3D execution graph
- See cost, tokens, artifacts, decisions, and failures per step
- Replay from any node — time-travel debugging for agents
- Compare runs side-by-side with `infini diff`

Inspectable agents. No more black boxes.

<br>

## Adapters

Adapters make the spec real for runtimes that already exist. The easiest external contribution is a new adapter.

```
adapters/
├── hermes/        ← Governance brain: policy, memory, escalation, audit
├── openclaw/      ← Execution runtime: browser, GitHub, terminal, filesystem
├── crewai/        ← Community
├── langgraph/     ← Community
├── mastra/        ← Community
├── goose/         ← Community
└── codex/         ← Community
```

Each adapter must pass the conformance suite: Parse, Run, Verify, Inspect, Replay.

Build one using the [Adapter SDK](sdk/).

<br>

## Key Features

```
 Mock mode        Run loops without API keys (CI & demos)
 CLI tools        validate · run · inspect · replay · diff · ui · benchmark
 Conformance      Adapters must pass strict tests
 12 Loops         Production-grade canonical patterns
 Adapter SDK      Add new engines in hours
 Zero-downtime    Works as a read-only overlay on existing systems
```

<br>

## Philosophy

```
Loops    >  Chains
Specs    >  Frameworks
Traces   >  Logs
Portable >  Lock-in
Correct  >  Fast
```

Read the full [Manifesto](MANIFESTO.md).

<br>

## Install

```bash
pip install infini-cli
```

Or from source:

```bash
git clone https://github.com/NickAiNYC/infini
cd infini/cli && pip install -e .
```

<br>

## CLI Reference

```bash
infini validate loop.yaml     # Check a Loopfile against the spec
infini run loop.yaml           # Execute a loop
infini run loop.yaml --mock    # Execute with mock adapter (no API key)
infini inspect run.json        # Open trace in terminal
infini ui run.json             # Launch Observatory UI
infini replay run.json         # Time-travel replay
infini diff v1.yaml v2.yaml    # Semantic diff between Loopfiles
infini benchmark loop.yaml     # Run standardized benchmarks
infini engines                 # List available adapters
infini init                    # Scaffold a new Loopfile
```

<br>

## Project Structure

```
infini/
├── spec/              Loopfile specification, grammar, JSON schema, RFCs
├── cli/               Reference CLI implementation
├── sdk/               Adapter SDK for third-party engines
├── adapters/          Hermes, OpenClaw, and community adapters
├── loops/             12 canonical loop patterns
├── examples/          Golden examples with traces
├── observatory-ui/    Next.js + React Three Fiber dashboard
├── docs/              Handbook, patterns, anti-patterns
├── benchmarks/        Standardized benchmark suite
├── registry/          Local registry and protocol
├── marketplace/       Category browser (preview)
├── prompts/           Loop Engineer prompt
└── ci/                GitHub Action for CI integration
```

<br>

## The Lineage

<div align="center">

```
Docker      standardized   containers
Terraform   standardized   infrastructure
OpenAPI     standardized   APIs
Markdown    standardized   documents
INFINI      standardizes   autonomous work
```

</div>

<br>

## Community

- [Discussions](https://github.com/NickAiNYC/infini/discussions) — questions, ideas, show & tell
- [RFCs](spec/rfcs/) — propose spec changes
- [Contributing](CONTRIBUTING.md) — how to get involved
- [Code of Conduct](CODE_OF_CONDUCT.md) — Contributor Covenant 2.1

<br>

## Next Steps

- Run a [golden example](examples/) in mock mode
- Read the [12 canonical loops](loops/)
- Explore the [spec](spec/loopfile-v1.md) and [RFCs](spec/rfcs/)
- Build an adapter using the [SDK](sdk/)
- Read the [Handbook](docs/handbook/)

<br>

---

<div align="center">

**Star if you want agents to be portable and inspectable.**

Built for the agent ecosystem. Spec is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). Code is [MIT](LICENSE).

<br>

<sub>Loops that don't end. Loops that improve.</sub>

</div>
