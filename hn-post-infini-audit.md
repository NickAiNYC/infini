# Show HN: INFINI — Audit your agent project for loop portability (0-100 score)

I built a CLI tool called INFINI. It does two things:

1. `infini audit ./my-project` — scans your project for agent-loop infrastructure and returns a 0-100 readiness score with specific fixes
2. `infini init --pattern daily-triage` — scaffolds a complete working agent loop from 5 canonical patterns

The underlying spec (Loopfile.yaml) declares what your agent loop does — not how one specific framework does it. Currently runs on 2 engines (Reference + LangGraph in mock mode), with adapter manifests ready for 5 more (CrewAI, AutoGen, Mastra, Hermes, OpenClaw). The adapter code itself is the next layer to ship.

## What `infini audit` does

It checks your project for 12 signals that indicate whether you have a production-ready agent loop or just a script:

```
$ infini audit ./my-project

  Score:    55/100 (55.0%)
  Maturity: L2 Assisted

✓ Found (6):
  +15 loopfile             Found: Loopfile.yaml
  +10 state                Found: STATE.md
  +12 verifier             Loopfile has a verifier/critic agent
  + 8 loop_config          Found: LOOP.md
  + 8 conventions          Found: AGENTS.md
  + 2 lessons              Found: lessons.md

✗ Missing (6):
  - 8 safety               Add a SAFETY.md documenting safety constraints
  -10 mcp_config           Add MCP tool declarations: .mcp.json or TOOLS block
  - 7 budget               Add a loop-budget.md documenting token spend
  -10 ci                   Add a GitHub Actions workflow in .github/workflows/
  - 8 activity             Run a loop to generate activity proof
  - 2 replay_trace         Run a loop to generate a run.json trace

Suggested next steps:
  → Add a SAFETY.md documenting safety constraints
  → Add MCP tool declarations
  → Add a loop-budget.md documenting token spend
```

Maturity levels: L0 Draft (0-24), L1 Report-only (25-49), L2 Assisted (50-74), L3 Unattended (75-100). Exit code 0 if score ≥ 50, 1 otherwise — usable as a CI gate.

## The Loopfile spec

A Loopfile is a declarative YAML file that defines what your agent loop does, not how one framework does it:

```yaml
LOOPFILE: "1.0"
name: daily-triage
version: 1.0.0
OBJECTIVE: Triage new issues and PRs from the last 24 hours.

AGENTS:
  - { name: triager, role: researcher, model_tier: sonnet, tools: [github] }
  - { name: labeler, role: builder, model_tier: haiku, tools: [github] }
  - { name: verifier, role: verifier, model_tier: haiku, tools: [github] }

STEPS:
  - { id: s1, name: fetch_new,   action: github.list_new, uses: triager, produces: [new-items.json] }
  - { id: s2, name: classify,    action: github.classify, uses: labeler, depends_on: [s1], produces: [triaged.json] }
  - { id: s3, name: verify,      action: github.verify_labels, uses: verifier, depends_on: [s2] }

VERIFY:
  syntactic: ["new-items.json:exists", "triaged.json:valid_json"]
  semantic: ["judge:triage_accuracy>=85"]
  confidence_threshold: 85

BUDGET: { dollars: 2, minutes: 10 }
STOP_WHEN: [all_verify_passed, iterations>=2]
```

The trace format (`run.json`) is identical between the 2 working engines — that's the portability thesis, partially validated.

## What's actually verified

I want to be precise because HN will ask:

**Verified:**
- 25 unit tests, 8 conformance tests — all passing
- `infini audit` works on real directories (tested on empty, partial, and fully-equipped projects)
- `infini init --pattern` scaffolds 5 working patterns (daily-triage, pr-babysitter, ci-sweeper, issue-triage, changelog-drafter) that parse as valid Loopfiles
- Real filesystem verification — `infini run --work-dir /path` actually stats files and checks content (not RNG or mock-passing)
- 2-engine portability in mock mode — same Loopfile produces identical trace structure on Reference and LangGraph engines
- Budget enforcement — stops execution when cost cap is hit
- Time-travel replay, trace diff, conformance suite

**NOT verified (being honest):**
- Live mode execution (real LLM API calls). Everything works in mock mode with deterministic output. Live mode might produce different step outputs across engines — I haven't tested this because I don't have API keys configured for it. This is the next milestone.
- The 5 adapters with manifests only (CrewAI, AutoGen, Mastra, Hermes, OpenClaw). The routing code accepts them as `--engine` flags but the adapter Python modules aren't wired yet. The manifests declare capabilities; the runtime needs to be built. Contingent on interest — I'll prioritize whichever adapter people actually want.
- Production use. Zero users so far. That's why I'm posting here.

## What I want from HN

1. **Run `infini audit` on your agent project.** Tell me if the score is meaningful or if the 12 signals are wrong. They're my guess — your feedback will sharpen them.

2. **Run `infini init --pattern daily-triage` and try to actually run the loop.** Tell me where it breaks. The patterns are templates, not production code — they need real-world pressure testing.

3. **If you use LangGraph, try `infini run Loopfile.yaml --mock --engine langgraph` and check whether the trace matches the Reference engine.** I need to know if the portability claim holds beyond my test suite.

## Getting started

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
pip install -e './cli[dev]'
infini audit .
infini init --pattern daily-triage
infini run Loopfile.yaml --mock
```

PyPI package coming once I have a real user confirm the installation flow works. For now, clone and run.

## What's next (if this gets traction)

- Wire the 5 adapter manifests into working runtimes (I'll build whichever one people actually ask for)
- Live-mode cross-engine verification (the honest gap above)
- One real production case study (I need one user for this)

I'm not building more features until I have user feedback driving priorities. The feature list is long enough. The gap is adoption, not code.

Ask me anything. I'll be honest about what works and what doesn't.
