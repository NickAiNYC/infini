# Portability Case Study: Scrutexity Claim Audit

## Source workflow

This Loopfile is modeled on an internal Scrutexity **Claim Audit Prompt Chain** — a 5-step workflow for auditing public website claims:

1. **Extract** — List every assertion from the target page verbatim
2. **Classify** — Label each claim per the Claim Classification Standard
3. **Proof gaps** — Identify missing evidence for unsupported claims
4. **AI reality check** — Run the AI distortion detection
5. **Emit findings** — Output 3-5 prioritized findings

Source: `GEM/02-PROMPTS/Claim Audit Prompt Chain.md`

## Loopfile

```yaml
LOOPFILE: "1.0"
name: scrutexity-claim-audit
OBJECTIVE: Produce a structured claim audit of the target URL.

AGENTS:
  - { name: extractor,  role: researcher, model_tier: sonnet }
  - { name: classifier, role: builder,    model_tier: sonnet }
  - { name: analyst,    role: researcher, model_tier: sonnet }
  - { name: verifier,   role: verifier,   model_tier: haiku  }

STEPS:
  - { id: s1, name: extract-claims,     action: web.extract_assertions,   uses: extractor,  produces: [extracted-claims.json] }
  - { id: s2, name: classify-claims,    action: claims.classify,          uses: classifier, depends_on: [s1], produces: [classified-claims.json] }
  - { id: s3, name: identify-proof-gaps, action: claims.identify_gaps,    uses: analyst,    depends_on: [s2], produces: [proof-gaps.json] }
  - { id: s4, name: ai-reality-check,   action: claims.ai_distortion_check, uses: analyst,  depends_on: [s2], produces: [ai-distortion.json] }
  - { id: s5, name: emit-findings,      action: findings.emit,            uses: extractor,  depends_on: [s3, s4], produces: [findings.md, audit/findings.json] }

VERIFY:
  syntactic:
    - "extracted-claims.json:exists"
    - "classified-claims.json:valid_json"
    - "proof-gaps.json:valid_json"
    - "findings.md:exists"
    - "audit/findings.json:valid_json"
  semantic:
    - "judge:extraction_completeness>=80"
    - "judge:classification_accuracy>=85"
    - "judge:findings_prioritization>=85"
  confidence_threshold: 80

BUDGET: { dollars: 5, minutes: 30 }
STOP_WHEN: [all_verify_passed, iterations>=3]
```

## Test results

### Reference engine

```bash
infini run Loopfile.yaml --mock -o runs/reference
```

```
✓ shipped. trace: runs/reference/run.json
```

### LangGraph engine

```bash
infini run Loopfile.yaml --mock --engine langgraph -o runs/langgraph
```

```
✓ shipped (langgraph). trace: runs/langgraph/run.json
```

### Trace diff

```bash
infini diff runs/reference/run.json runs/langgraph/run.json
```

```
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Metric     ┃ Reference ┃ LangGraph ┃  Delta ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Outcome    │ verified │ verified │        │
│ Iterations │        2 │        1 │        │
│ Steps      │       10 │        5 │        │
│ Cost       │    $0.17 │    $0.09 │ $-0.08 │
│ Time       │    11.2m │     6.4m │  -4.8m │
└────────────┴──────────┴──────────┴────────┘
```

## What matched

- Same Loopfile executed on both engines
- Same step graph
- Same dependency order
- Same artifact names
- Same verification outcome
- Same trace schema

## What differed

- Runtime implementation
- Timing
- Engine metadata
- Mock output text

## What this proves

A real-world, multi-step workflow can be represented once as a Loopfile and executed across supported runtimes while preserving comparable traces.

## What this does not prove yet

- Live LLM parity
- Tool-call parity
- Production readiness
- Equivalence across CrewAI, AutoGen, or Mastra

Full traces: [reference](runs/reference/run.json), [langgraph](runs/langgraph/run.json)
