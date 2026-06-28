# INFINI

**The Open Standard for Agent Portability**

Write your agent logic **once**. Execute it on **any** framework. Verify it actually worked.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
[![Stars](https://img.shields.io/github/stars/NickAiNYC/infini?style=social)](https://github.com/NickAiNYC/infini)

> **Agents just got their Docker moment.**
> Stop rewriting your workflows every time you change runtimes.

[Install](#install) · [Quickstart](#quickstart) · [Observatory](#the-local-observatory) · [Manifesto](MANIFESTO.md) · [Spec](spec/loopfile-v1.md) · [Roadmap](ROADMAP.md)

![INFINI Demo](assets/demo.gif)

---

## The Problem

Current agent frameworks create **massive vendor lock-in**.

Your core logic gets entangled with LangChain, CrewAI, AutoGen, OpenAI Agents SDK, etc. Switching runtimes means rewriting everything. Traces are opaque. Verification is an afterthought. Migration debt compounds.

**INFINI is the escape hatch.**

## The Solution: The Loopfile

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

## Quickstart (under 60 seconds)

```bash
pip install infini-cli

# Clone and try a golden example (no API key needed)
infini run examples/golden-research-assistant/research-loop.yaml --mock

# Launch the 3D Observatory
infini ui runs/latest/run.json
```

## The Local Observatory

Every run produces a standardized trace. The Observatory is a beautiful local Next.js + React Three Fiber dashboard:

- Drop in a `.trace` file
- Interactive 3D execution graph (rotate, zoom, click)
- See cost, tokens, artifacts, decisions, and failures per step
- Replay from any node

<p align="center">
  <img src="assets/observatory-ui.png" alt="INFINI Observatory — 3D execution graph" />
</p>

Inspectable agents. No more black boxes.

## Key Features

- **Mock mode** — run loops without API keys (perfect for CI & demos)
- **CLI tools** — `validate`, `run`, `inspect`, `replay`, `diff`, `ui`, `engines`, `init`, `new`, `graph`, `benchmark`
- **Conformance suite** — adapters must pass strict tests
- **12 Canonical Loops** — production-grade patterns
- **Adapter SDK** — easy to add new engines
- **Zero-downtime adoption** — works as a read-only overlay

## Philosophy

```
Loops > Chains
Specs > Frameworks
Traceability > Magic
Portability > Lock-in
Correctness > Raw speed
```

Read the full [Manifesto](MANIFESTO.md).

## Install

```bash
pip install infini-cli
```

Or from source:

```bash
git clone https://github.com/NickAiNYC/infini
cd infini/cli && pip install -e .
```

## Next Steps

- Try the [golden examples](examples/)
- Explore the [12 canonical loops](loops/)
- Read the [spec](spec/loopfile-v1.md) and [RFCs](spec/rfcs/)
- Build an adapter using the [SDK](sdk/)

---

**Star if you want agents to be portable and inspectable.**

Built for the agent ecosystem.
