# Portability Proof

Same Loopfile. Two engines. Identical outcomes.

## Test: verifier-test

```yaml
LOOPFILE: "1.0"
name: verifier-test
OBJECTIVE: Test the real verifier
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS:
  - { id: s1, name: noop, action: noop, uses: builder }
VERIFY:
  syntactic:
    - "output.txt:exists"
    - "output.txt:contains:hello"
    - "output.txt:contains:goodbye"
  semantic: []
  confidence_threshold: 80
BUDGET: { dollars: 1, minutes: 10 }
STOP_WHEN: [all_verify_passed, iterations>=1]
```

## Commands

```bash
infini run verifier-test.yaml --mock -o runs/infini-trace
infini run verifier-test.yaml --mock --engine langgraph -o runs/langgraph-trace
infini diff runs/infini-trace/run.json runs/langgraph-trace/run.json
```

## Diff output

```
INFINI diff — Traces

┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Metric     ┃       v1 ┃       v2 ┃  Delta ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Outcome    │ verified │ verified │        │
│ Iterations │        1 │        1 │        │
│ Steps      │        1 │        1 │        │
│ Cost       │    $0.01 │    $0.01 │ +$0.00 │
│ Time       │     0.5m │     1.5m │  +1.0m │
└────────────┴──────────┴──────────┴────────┘
```

## What is identical

- **Outcome**: both report `verified`
- **Step count**: both execute 1 step
- **Iterations**: both complete in 1 iteration
- **Step IDs**: both use `s1`
- **Trace schema**: both produce `run.json` with the same structure (`loopfile`, `engine`, `steps`, `cost`, `verifications`)
- **Verification result**: both pass/fail the same checks identically

## What is not identical (expected)

- **Token counts**: differ due to deterministic RNG seeded per engine name
- **Cost**: minor variation from different token counts
- **Wall time**: minor variation from mock execution path differences
- **Implementation internals**: Reference engine calls `_execute_step` directly; LangGraph adapter builds a state graph

## What this proves

A Loopfile written once produces the same logical execution trace on two different engine implementations. The trace schema is stable across engines, which means tooling (diff, replay, observatory) works identically regardless of which engine ran the loop.

## What it does not prove yet

- Live mode (real LLM calls) — mock mode uses deterministic RNG; real LLMs may produce different step outputs across engines
- Complex DAGs — only tested linear step sequences so far
- Parallel execution — not yet tested across engines
- Production workloads — zero users, zero production runs
