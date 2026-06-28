# Launch Materials

Ready-to-post content for the INFINI public launch. Copy-paste, don't edit.

---

## X Thread (5 tweets)

### Tweet 1 — The hook

```
same loop. three engines. zero code changes.

infini run loop.yaml --engine=infini
infini run loop.yaml --engine=hermes
infini run loop.yaml --engine=openclaw

the Dockerfile for AI agents. open standard, not another framework.

github.com/NickAiNYC/infini
```

### Tweet 2 — The problem

```
LangChain. CrewAI. AutoGen. OpenAI Agents SDK.

100 frameworks. zero standards. every team that switches rewrites everything.

INFINI is the Loopfile — a portable spec for agent loops. write once, run on any engine.

github.com/NickAiNYC/infini
```

### Tweet 3 — The demo

```
every agent run leaves a trace.

infini ui renders it as a 3D node graph — rotate, zoom, click any node, see the cost and tokens at that millisecond.

this is what "inspectable AI" looks like.

github.com/NickAiNYC/infini
```

### Tweet 4 — The ecosystem

```
INFINI is not production infrastructure yet.

it's an early open standard with:
→ working CLI (mock mode, no API key)
→ conformance suite (8/8 passing)
→ adapter certification (hermes + openclaw)
→ adapter SDK (build one in 30 min)
→ eternal memory (SQLite FTS5)
→ 3-agent orchestration

github.com/NickAiNYC/infini
```

### Tweet 5 — The ask

```
looking for the first CrewAI adapter.

and the first LangGraph adapter.

and the first Mastra adapter.

one external adapter is worth more than five new RFCs. the SDK is ready. github.com/NickAiNYC/infini
```

---

## Hacker News Post

**Title:** INFINI: The Dockerfile for AI Agents (open standard, not a framework)

**Text:**

```
I've been building an open standard for portable AI agent loops. The idea: write your agent logic once as a declarative YAML (a "Loopfile"), run it on any framework — LangGraph, CrewAI, Hermes, OpenClaw — without rewriting code.

The problem: every agent framework reinvents the same primitives (state, verification, cost ceilings, replay) in incompatible ways. A loop written for LangChain is useless in CrewAI. Switching means a full rewrite.

The bet: the same separation Docker gave to containers — a portable format that any runtime can implement.

What's live today:
- Working CLI: pip install, validate, run (mock mode needs no API key)
- Conformance suite: 8/8 tests passing
- Adapter certification: Hermes and OpenClaw certified with honest percentages (70.8%, 66.7%)
- Adapter SDK: build an adapter in under 30 minutes
- Eternal memory: SQLite FTS5, verbatim storage, no summarization
- 3-agent orchestration: Planner/Worker/Inspector via SQLite coordination bus
- 3D Observatory: Next.js + React Three Fiber trace visualizer
- 10 canonical benchmark cases (the "ImageNet for agent loops")

What's not ready:
- Live LLM execution (API key required, provider-agnostic via MCP)
- No external adapters yet (Hermes and OpenClaw are reference implementations)
- Not on PyPI yet

This is early. I'm not claiming it's production-ready. I'm claiming the shape is right and the ecosystem foundation exists. What it needs now is one external adapter to prove portability works.

If you build agents and you're tired of framework lock-in, take a look. The SDK is ready.

https://github.com/NickAiNYC/infini
```

---

## Reddit Post (r/programming or r/MachineLearning)

**Title:** I built an open standard for portable AI agent loops (like Dockerfile but for agents)

**Text:**

```
INFINI is an open standard that lets you write agent logic once and run it on any framework — without rewriting code.

The core idea: a declarative YAML called a "Loopfile" that any conforming engine can parse, run, verify, inspect, replay, and diff. Same YAML, any engine.

Think: Dockerfile for AI agents. Not another framework. A portability layer above frameworks.

What works today:
- CLI with mock mode (no API key needed to try it)
- 8/8 conformance tests passing
- Hermes and OpenClaw adapters certified
- Adapter SDK (build one in 30 minutes)
- SQLite-based eternal memory with FTS5 search
- 3-agent orchestration (Planner/Worker/Inspector)
- 3D trace visualizer (Next.js + React Three Fiber)
- 10 canonical benchmark cases

What's honest:
- Not production-ready yet
- No external adapters (the two certified ones are reference implementations)
- Not on PyPI yet
- Live LLM execution needs an API key

What I'm looking for:
- The first external adapter (CrewAI, LangGraph, Mastra, etc.)
- Feedback on the spec
- Contributors who want to build the ecosystem

The repo: https://github.com/NickAiNYC/infini

I'd rather have one real external adapter than 100 more files in the repo. If you've ever been burned by agent framework lock-in, this is for you.
```

---

## Launch Article (for blog / Medium / dev.to)

```markdown
# Why I Built INFINI: The Open Standard for Agent Portability

Every AI engineering team I've talked to has the same problem: vendor lock-in at the agent layer.

You build a complex agent workflow in LangChain. Six months later, you want to try CrewAI. You discover that your core business logic is deeply entangled with LangChain's memory handlers, routing conventions, and telemetry schema. Switching means a complete rewrite. Not switching means living with LangChain's limitations forever.

This isn't a technology problem. It's a standards problem.

Docker solved this for containers. Terraform solved it for infrastructure. OpenAPI solved it for APIs. Each won by being boring, portable, and open.

I built INFINI to do the same for autonomous agent loops.

## What is INFINI?

INFINI is a declarative portability layer for AI agents. You write your agent logic once as a "Loopfile" — a YAML file that declares the objective, the agents, the steps, the verification criteria, the budget, and the stop conditions. Any conforming engine can run it.

The key insight: separate the *what* (the Loopfile) from the *how* (the engine). Your business logic lives in the Loopfile. The engine is replaceable. Switching engines is a one-line change.

## What's in the repo

- **A working CLI** with mock mode (no API key needed)
- **8/8 conformance tests** passing
- **Adapter certification** — Hermes and OpenClaw certified with honest percentages
- **An Adapter SDK** — build an adapter in under 30 minutes
- **Eternal memory** — SQLite FTS5, verbatim storage, no summarization
- **3-agent orchestration** — Planner/Worker/Inspector via SQLite coordination bus
- **A 3D Observatory** — trace visualization in Next.js + React Three Fiber
- **10 canonical benchmark cases** — the "ImageNet for agent loops"
- **Native MCP support** in the spec (Model Context Protocol)

## What's honest

INFINI is not production infrastructure. It's an early open standard with a working CLI, a conformance suite, and an adapter SDK. The two certified adapters (Hermes and OpenClaw) are reference implementations — I built them. The real validation comes when someone else builds one.

That's the milestone I'm working toward: one external adapter. One independent developer who looks at the SDK and says "I can build this in 30 minutes" — and does.

## The bet

Engines will keep multiplying. Models will keep getting cheaper. Verification will become the bottleneck. Portability will win.

The team that owns the portable format owns the category. I'm trying to be that team — openly, honestly, and without hype.

The repo is at https://github.com/NickAiNYC/infini. If you build agents and you're tired of framework lock-in, take a look. The SDK is ready.
```

---

## Product Hunt (when ready)

**Tagline:** The Dockerfile for AI agents — write once, run on any framework.

**Description:**

```
INFINI is an open standard for portable AI agent loops. Write your agent logic as a declarative Loopfile (YAML), run it on any conforming engine — LangGraph, CrewAI, Hermes, OpenClaw — without rewriting code.

Same YAML. Any engine. Full traceability.

Features:
- Working CLI with mock mode (no API key needed)
- 8/8 conformance tests passing
- Adapter certification (Hermes + OpenClaw)
- Adapter SDK (build one in 30 minutes)
- Eternal memory (SQLite FTS5)
- 3-agent orchestration
- 3D trace Observatory
- Native MCP support

Early stage. Not production-ready. Looking for the first external adapter to prove portability works.
```
