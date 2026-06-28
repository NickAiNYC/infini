# RFC-0010: Cost Accounting

- Start date: 2026-06-28
- Status: draft
- Spec version: 1.0 (BUDGET), 1.1 (rich accounting)
- PR: TBD
- Implementation: `BUDGET` enforcement in 1.0; rich accounting in 1.1

## Summary

Defines how INFINI accounts for cost. Every loop has a budget; the engine
enforces it; the trace records what was spent. Cost is a first-class
concern, not an afterthought.

## Motivation

Agent runs cost money. Without explicit budgets, runs spiral: a stuck loop
spends $100 on retries before anyone notices. The BUDGET block is the
discipline that prevents this.

Cost accounting must be:

- **Declared.** A loop without a budget doesn't run. Period.
- **Multi-dimensional.** Dollars, wall-clock minutes, and tokens are all
  tracked. Any one can abort the loop.
- **Attributable.** Cost is attributed to the step that incurred it, not
  just to the loop as a whole.
- **Visible.** Cost is shown in the trace, in the Observatory, and in the
  CLI output. There are no surprise bills.

## Detailed design

### The BUDGET block

```yaml
BUDGET: { dollars: 5, minutes: 15, tokens: 500000 }
```

- `dollars` and `minutes` are required. `tokens` is optional.
- The engine must abort the loop and mark the run `budget_exceeded` if
  any ceiling is breached.
- Partial work is preserved in the trace for replay.

### Per-step attribution

Every step in the trace carries its cost:

```json
{
  "id": "s2",
  "name": "edit",
  "cost": {
    "dollars": 0.34,
    "minutes": 1.20,
    "tokens": { "input": 4200, "output": 1100, "total": 5300 }
  }
}
```

This is what makes the Observatory's cost waterfall possible.

### The cost model

Engines translate `model_tier` into actual dollar costs using a pluggable
cost model. The reference engine ships with a cost model for common
models (Claude, GPT, Gemini). Adapters can override the cost model for
their engine.

The cost model is **not** part of the Loopfile. A Loopfile says
`model_tier: sonnet`; the engine's cost model knows what sonnet costs
today. This keeps Loopfiles portable across model price changes.

### Budget policy

The Hermes adapter adds a `governance.budget_policy` field:

| Policy | Behavior |
| --- | --- |
| `strict` | Exceeding any ceiling aborts the run. Default. |
| `advisory` | Exceeding a ceiling warns but does not abort. |
| `off` | No enforcement. For development only. |

The reference engine supports `strict` only. `advisory` and `off` are
governance features.

### Budget tracking

The engine tracks budget consumption in real time. At 80% of any ceiling,
it fires a `budget_warning` event visible in the Observatory. At 100%, it
aborts.

```json
{
  "budget": {
    "dollars": { "spent": 4.21, "ceiling": 5.00, "pct": 84 },
    "minutes": { "spent": 12.5, "ceiling": 15,   "pct": 83 },
    "tokens":  { "spent": 410000, "ceiling": 500000, "pct": 82 }
  },
  "events": [
    { "at": "2026-06-28T10:46:11Z", "kind": "budget_warning", "ceiling": "dollars", "pct": 80 }
  ]
}
```

### Cross-iteration accounting

For multi-iteration loops, cost accumulates across iterations. The budget
is for the whole run, not per iteration. This is intentional — a loop
that needs 6 iterations to converge should fit in one budget, not 6.

### Cost in replay

Replay inherits the original run's budget. If you replay from step N, the
budget already spent in steps 1..N is "sunk"; the replay only has the
remaining budget.

You can override this with `--fresh-budget` to give the replay a full
budget. This is useful for testing "would this loop have shipped if we'd
started fresh at step N?"

## Alternatives considered

- **No budget enforcement (developer's problem).** Rejected — this is the
  status quo and it leads to surprise bills.
- **Per-iteration budgets.** Rejected — encourages loops that don't
  converge. The whole-run budget forces the loop author to think about
  convergence.
- **Single dimension (dollars only).** Rejected — minutes and tokens
  matter independently. A loop might be cheap in dollars but slow in
  minutes.
- **Cost model in the Loopfile.** Rejected — couples Loopfiles to
  specific model pricing, breaking portability across price changes.

## Backwards compatibility

v1.0. `BUDGET` is required in every v1.0 Loopfile. Engines that don't
enforce it are not conformant.

## Conformance impact

The `Run Loop` conformance capability requires the engine to enforce
`BUDGET`. The `Inspect Trace` capability requires the engine to emit
per-step cost in `run.json`.

## Open questions

- Should budgets support per-step ceilings (not just whole-loop)?
  Current answer: no, keep it simple. Revisit at v1.1.
- Should budgets support "soft ceilings" (warn at 80%, abort at 100%)?
  Current answer: the 80% warning is automatic; the abort policy is
  governed by `budget_policy`.
- How are cached model responses costed in replay? Current answer: at
  zero. Cache hits are free.

## Future possibilities

- v1.1: per-step budget ceilings.
- v1.2: budget forecasting — the Observatory predicts whether the loop
  will fit in budget based on iteration 1's spend.
- v2.0: budget packs — pre-purchased budgets that span multiple loops
  (useful for teams).

## Acknowledgements

The cost model is borrowed from CloudWatch billing (multi-dimensional
budgets), Datadog (per-resource attribution), and the SRE Book (error
budgets as a discipline).
