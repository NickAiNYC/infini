# INFINI Demo — 60 Seconds

One workflow. Four engines. Identical traces.

---

## The problem

You built an agent for LangGraph. Now you want to run it on CrewAI.
Or test it with a local model. Or give it to a team that uses a
different framework.

Every framework has its own format. Moving between them means
rewriting orchestration logic.

## The fix

INFINI separates the workflow from the runtime. You write a **Loopfile**
once. It runs on any engine.

## The demo

### The Loopfile

```yaml
LOOPFILE: "1.0"
name: squad-collab
description: "Plan, research, implement, verify — on any engine."

AGENTS:
  - { name: planner, role: planner, model_tier: sonnet }
  - { name: verifier, role: verifier, model_tier: haiku }

STEPS:
  - id: s1
    name: plan
    uses: planner
    action: write_spec
    produces: [plan.md]
  - id: s2
    name: verify
    uses: verifier
    action: check_results
    depends_on: [s1]
    produces: [verify-report.json]

VERIFY:
  syntactic: ["plan.md:exists", "verify-report.json:exists", "verify-report.json:contains:pass"]
  semantic: []
  confidence_threshold: 0

BUDGET: { dollars: 5, minutes: 10 }
STOP_WHEN: ["all_verify_passed"]
```

### Run it on 4 engines

```bash
infini run loop.yaml --engine infini --trace ref.json
infini run loop.yaml --engine langgraph --trace lg.json
infini run loop.yaml --engine local --trace local.json
infini run loop.yaml --engine codemap --trace codemap.json
```

### The result

```bash
infini diff ref.json lg.json
# → Identical trace structure. Verified. Portable.

infini diff lg.json local.json
# → Identical trace structure. Verified. Portable.
```

Four engines. One Loopfile. Same trace shape.

---

## What you just saw

| Before INFINI | After INFINI |
|---------------|--------------|
| Write workflow for LangGraph | Write one Loopfile |
| Rewrite for CrewAI | Run same Loopfile on CrewAI engine |
| Rewrite for local testing | Run same Loopfile on local engine |
| Manually compare outputs | `infini diff` shows identical structure |
| No verification | `VERIFY` block checks real files |
| No budget control | `BUDGET` caps cost and time |

---

## Try it yourself

```bash
pip install infini-cli
git clone https://github.com/NickAiNYC/infini
cd infini
infini run examples/squad-loop/Loopfile.yaml --engine infini --mock
infini run examples/squad-loop/Loopfile.yaml --engine langgraph --mock
infini diff runs/reference/run.json runs/langgraph/run.json
```

5 minutes. No API keys. No account.

[Full tutorial](tutorial.md) · [Comparison](comparison.md) · [GitHub](https://github.com/NickAiNYC/infini)
