# INFINI — Portable Agent Loop Spec

> Write agent logic once. Run it on 4 engines. Verify it for real.

**GitHub:** [github.com/NickAiNYC/infini](https://github.com/NickAiNYC/infini)

---

## The problem

Today, moving an agent workflow between frameworks means rewriting
orchestration logic. Define it for LangGraph? You're locked in.
Claude Code? Different format. Local LLM? Good luck porting.

There is no portable, verifiable format for agent collaboration.

## What INFINI is

INFINI is a specification and CLI for defining agent workflows as
**Loopfiles** — portable YAML that runs on multiple engines and
produces comparable execution traces.

One Loopfile. Four engines. Identical trace structure.

## Two headline claims (both literally true)

**Claim 1: "Write once, run on 4 engines"**

```bash
infini run loop.yaml --engine infini     # Reference engine
infini run loop.yaml --engine langgraph  # LangGraph
infini run loop.yaml --engine local      # Qwythos (offline LLM)
infini run loop.yaml --engine codemap    # Context-aware

infini diff ref.json local.json
# → "Identical trace structure. Verified. Portable."
```

**Claim 2: "Verify it for real"**

```yaml
VERIFY:
  syntactic:
    - "auth.py:exists"            # Actually checks filesystem
    - "test-output.log:contains:✅"  # Actually reads file content
    - "pytest tests/:exit_zero"   # Actually runs the command
```

No RNG. No mock-passing. Every `:exists`, `:contains`, `:exit_zero`
check hits the real filesystem or subprocess. If the file doesn't
exist, verification fails.

## Engine matrix

| Engine | Mock | Live | Context-Aware | Offline | Cost |
|--------|------|------|---------------|---------|------|
| Reference | ✅ | ⚠️ | ❌ | ✅ | $0 |
| LangGraph | ✅ | ✅ | ❌ | ❌ | $ |
| Local (Qwythos) | ❌ | ✅ | ❌ | ✅ | $0 |
| **Codemap** | ❌ | ✅ | **✅** | ✅ | $0 |

## Quickstart

```bash
pip install infini-cli
# or: git clone + pip install -e './cli[dev]'

echo 'LOOPFILE: "1.0"
name: verify-me
OBJECTIVE: "Show portability."
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS: []
VERIFY:
  syntactic:
    - "README.md:exists"
  semantic: []
  confidence_threshold: 80
BUDGET: { dollars: 1, minutes: 2 }
STOP_WHEN: ["all_verify_passed"]' > loop.yaml

infini run loop.yaml --live
# → reads real README.md, checks it exists, passes verification
```

## The story behind it

An audit scored INFINI at 41/100. The biggest criticisms:

- "Mock-only, no real engine"
- "Portability proof is two mocks"
- "Verification is RNG"
- "No open-weight model support"
- "No context-awareness"

Over the last week, every one of those has been addressed:

| Criticism | Fix |
|-----------|-----|
| Mock-only | 4 engines: Reference, LangGraph, Local, Codemap |
| Portability is two mocks | All 4 engines produce identical traces |
| Verification is RNG | Real filesystem + subprocess checks |
| No open-weight model | Qwythos-9B GGUF runs fully offline |
| No context-awareness | Codemap injects project intelligence |

Score today: **~75/100**.

## Market validation

The "loop engineering" thesis has over **2.2M views** on X. The community
is already thinking in INFINI terms — they just don't have a portable
format for it yet.

| Loop Engineering Concept | INFINI Implementation |
|--------------------------|----------------------|
| "Define the goal; the loop discovers, plans, executes, verifies" | `OBJECTIVE` + `STEPS` + `VERIFY` |
| "Maker and checker should not be the same agent" | `AGENTS` list + `VERIFY` block separates executor from reviewer |
| "Memory lets a loop continue across runs" | `memory: persist: true` + FTS5 retrieval |
| "Skills are reusable project knowledge" | `SKILL.md` files imported via `skills:` field |
| "Worktrees for parallel agents" | `--work-dir` + `--engine codemap` for context isolation |
| "Plugins and connectors" | MCP tools + `tools:` in Loopfile |
| "The loop starts automatically" | INFINI Guard GitHub Action |
| "Cheap long-context models make loops practical" | Local engine (Qwythos) for $0 dev, `BUDGET` caps live costs |

Loop engineering is the AI skill every builder needs in 2026.
**INFINI is the open standard that makes it portable, verifiable,
and affordable.**

## What's NOT ready

- 3 of 6 adapters (CrewAI, AutoGen, Mastra) — CLI accepts `--engine`
  but runtime isn't wired
- Production use. Zero real users. The repo is public for feedback,
  not deployment.
- The Observatory UI renders mock data until live trace ingestion
  is implemented.

## How to contribute

- **Adapters** — Help wire CrewAI, AutoGen, Mastra. The manifests
  exist; the runtime needs building.
- **Live mode testing** — Run the same Loopfile on two engines in
  live mode and post the trace diff.
- **Feedback** — Open an issue. Tell me what's wrong, what's missing,
  or what's confusing.

[GitHub](https://github.com/NickAiNYC/infini) ·
[Spec](https://github.com/NickAiNYC/infini/blob/main/spec/loopfile-v1.md) ·
[Contributing](https://github.com/NickAiNYC/infini/blob/main/CONTRIBUTING.md)

---

*MIT licensed. Spec is CC-BY-4.0. Code is MIT.*
