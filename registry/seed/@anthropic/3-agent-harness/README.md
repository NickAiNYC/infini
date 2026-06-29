# @anthropic/3-agent-harness

> The flagship INFINI reference loop. A production-grade implementation of Anthropic Research Engineering's internal 3-agent coding harness.

**Category:** Coding / Autonomous Systems
**Tier:** Gold (100% conformance)
**Cost:** ~$1,000/day autonomous
**Install:** `infini registry install @anthropic/3-agent-harness@1.0.0`

---

## What this implements

Anthropic's internal harness runs a 6-layer loop with 3 specialized agents:

```
Plan → Build → Test → Reject → Repair → Improve
```

| Layer | Agent | What happens |
|-------|-------|-------------|
| **Plan** | Planner (Opus) | Turns a vague natural-language prompt into a concrete spec + task breakdown |
| **Build** | Generator (Sonnet) | Implements the spec in sprints, committing to git after each |
| **Test** | Evaluator (Sonnet) | Runs unit tests + **Playwright UI tests** via MCP |
| **Reject** | Evaluator | Evaluation gate: if tests fail, routes bug report back to Generator |
| **Repair** | Generator | Receives the specific bug report and fixes the exact issues |
| **Improve** | Generator | After all tests pass: refactors, adds docs, optimizes |

### The 3 agents

| Agent | Model | Role | MCP Tools |
|-------|-------|------|-----------|
| **Planner** | Opus | Turns vague prompts into specs | filesystem, shell |
| **Generator** | Sonnet | Builds in sprints, commits to git | filesystem, shell, git |
| **Evaluator** | Sonnet | QA agent — runs Playwright UI tests | filesystem, shell, Playwright |

### The startup sequence (Layer 0)

Before every session, the harness runs an expensive initialization:
- Spins up a Dockerized environment (`docker-compose.yml`)
- Sets environment variables (`.env`)
- Loads context from previous sessions (INFINI memory)

This is modeled as `s0_startup` — a mandatory step that all other steps depend on.

---

## The premature victory bug — and how INFINI prevents it

### The bug

Anthropic discovered that their Evaluator agent would declare the project "done" prematurely because it looked at **progress logs** (git commits, file changes) superficially instead of actually **running the UI tests**.

### The fix in this Loopfile

The `VERIFY` block explicitly guards against this:

```yaml
VERIFY:
  syntactic:
    - "playwright-report.json:exists"           # Report must exist
    - "playwright-report.json:tests_executed"    # Tests must have RUN
    - "playwright-report.json:exit_zero"         # Tests must PASS
    - "ui-screenshots/:non_empty"               # Screenshots must exist
  semantic:
    - "judge:evaluator_ran_ui_tests==true"       # Explicit: did it run tests?
```

The `judge:evaluator_ran_ui_tests==true` check is the direct guard. Even if the Evaluator says "done," the verification layer independently confirms that Playwright tests were actually executed — not just that the Evaluator claimed they were.

### Debugging the bug with time-travel replay

If the premature victory bug occurs, INFINI's time-travel replay lets you debug it precisely:

```bash
# 1. Run the harness
infini run loop.yaml --live --engine infini

# 2. The loop exits with "unverified" — the evaluator_ran_ui_tests check failed

# 3. Inspect the trace to see what happened
infini inspect runs/latest/

# 4. Time-travel to the test step (s3_test) — the moment of the bug
infini replay runs/latest/ --step s3_test

# 5. The replay opens an interactive session at s3_test.
#    You can see:
#    - What the evaluator agent received as input
#    - What tool calls it made (or didn't make)
#    - Whether it called playwright.run or just read git logs
#    - The exact prompt that led to the premature declaration

# 6. Mutate the inputs and replay to test a fix:
infini replay runs/latest/ --step s3_test --freeze-model-calls
# (bit-exact reproduction — same model responses, so you can verify
#  the bug is in the prompt, not the model)

# 7. Diff the original trace vs. a replay with a fixed prompt:
infini diff runs/latest/run.json runs/replay-s3-test/run.json
```

This is impossible in any other framework. LangGraph, CrewAI, and AutoGen have no time-travel replay. INFINI's trace + replay + diff is the only way to debug an agent that "lied" about running tests.

---

## Model-agnostic and framework-agnostic

### Model-agnostic

The Loopfile declares `model_tier` (haiku, sonnet, opus), not model names. The engine resolves the tier to whatever model you've configured:

```bash
# Run with Claude (default)
ANTHROPIC_API_KEY=sk-... infini run loop.yaml --live

# Run with GPT-4
OPENAI_API_KEY=sk-... infini run loop.yaml --live

# Run in mock mode (no API key, deterministic)
infini run loop.yaml --mock
```

The same Loopfile runs on any model. The Planner uses `opus` tier for complex reasoning; the Generator uses `sonnet` for cost-efficient coding; the Evaluator uses `sonnet` for balanced analysis.

### Framework-agnostic

```bash
# Run on INFINI Reference Engine
infini run loop.yaml --engine infini

# Run on LangGraph (when adapter ships)
infini run loop.yaml --engine langgraph

# Run on CrewAI (when adapter ships)
infini run loop.yaml --engine crewai
```

The Loopfile is the same. The engine is swappable. This is the Docker promise applied to agents.

---

## MCP tools

This loop uses 4 MCP servers:

| MCP Server | Purpose |
|------------|---------|
| `filesystem` | Read/write source files |
| `git` | Commit code after each sprint |
| `playwright` | UI testing — the Evaluator's primary tool |
| `sequential-thinking` | Multi-step reasoning for the Planner |

```yaml
TOOLS:
  - mcp: "github.com/modelcontextprotocol/servers/src/filesystem"
  - mcp: "github.com/modelcontextprotocol/servers/src/git"
  - mcp: "github.com/modelcontextprotocol/servers/src/playwright"
  - mcp: "github.com/modelcontextprotocol/servers/src/sequential-thinking"
```

---

## Cost monitoring

Anthropic estimates ~$1,000/day to run this autonomously. The Loopfile enforces this:

```yaml
BUDGET: { dollars: 1000, minutes: 1440, tokens: 10000000 }

ENGINE:
  cost_monitoring:
    daily_limit: ${COST_LIMIT:-1000}
    abort_on_exceed: true
    alert_at: 80%
```

The engine:
1. Tracks spend in real-time across all 3 agents
2. Alerts at 80% of the daily limit
3. Aborts at 100% — no surprise bills

Override with an environment variable:
```bash
COST_LIMIT=500 infini run loop.yaml --live  # lower limit for testing
```

---

## Installation

```bash
# Install from the INFINI Loop Registry
infini registry install @anthropic/3-agent-harness@1.0.0

# Run in mock mode (no API key, deterministic)
infini run ~/.infini/cache/@anthropic/3-agent-harness/1.0.0/loop.yaml --mock

# Run with a live LLM
infini run ~/.infini/cache/@anthropic/3-agent-harness/1.0.0/loop.yaml --live

# Run with 3-agent orchestration (Planner/Worker/Inspector)
infini run ~/.infini/cache/@anthropic/3-agent-harness/1.0.0/loop.yaml --plan

# Inspect the trace
infini inspect runs/latest/

# Time-travel replay from the test step
infini replay runs/latest/ --step s3_test
```

---

## Loop diagram

```
┌─────────────────────────────────────────────────────┐
│              STARTUP SEQUENCE (s0)                   │
│  Spin up Docker, set env vars, load context          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              PLAN (s1) — Planner (Opus)              │
│  Vague prompt → spec.md + task-breakdown.json        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              BUILD (s2) — Generator (Sonnet)         │
│  Implement spec in sprints, commit to git            │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              TEST (s3) — Evaluator (Sonnet)          │
│  Run unit tests + Playwright UI tests                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│        REJECT / EVALUATE (s4) — Evaluator            │
│  If tests fail → bug-report.md → route to Repair     │
│  If tests pass → route to Improve                    │
└──────────┬──────────────────┬────────────────────────┘
           │ (fail)           │ (pass)
           ▼                  ▼
┌──────────────────┐  ┌──────────────────────────────┐
│  REPAIR (s5)     │  │  IMPROVE (s6)                │
│  Generator fixes │  │  Generator refactors,        │
│  specific bugs   │  │  adds docs, optimizes        │
│  from bug-report │  │                              │
└────────┬─────────┘  └──────────────┬───────────────┘
         │                           │
         ▼                           ▼
    (loop back to s3_test)     (loop exits — verified)
```

---

## Files

- [`loop.yaml`](loop.yaml) — the Loopfile
- [`manifest.json`](manifest.json) — registry manifest
- [`README.md`](README.md) — this file

---

## Attribution

This loop is inspired by Anthropic Research Engineering's internal harness as described in their leaked write-up. The 6-layer architecture (Plan→Build→Test→Reject→Repair→Improve), 3-agent model (Planner/Generator/Evaluator), and the premature victory bug are all from their report. INFINI's contribution is the declarative Loopfile, time-travel replay debugging, and framework-agnostic portability.
