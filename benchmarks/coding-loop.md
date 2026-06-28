# Benchmark: Coding Loop

Loop: `infini/coding-loop@1.0`
Engines: INFINI Reference, Hermes, OpenClaw, LangGraph (when adapter ships)
Last run: planned

> This benchmark spec is final; the numbers are not yet populated. Once
> the adapters ship, this file will be updated with real results.

---

## Loop

The canonical [`coding-loop`](../loops/coding-loop/) — implement a
feature, preserve tests, open a PR.

## Inputs

10 fixture tasks of varying complexity:

- 3 trivial (single-file change, 1 test)
- 4 moderate (multi-file change, 3–5 tests)
- 3 complex (architecture-level change, 10+ tests)

Fixtures live in `benchmarks/fixtures/coding-loop/` (planned).

## Engines

Each engine runs all 10 fixtures, 10 times each (N=100 per engine).

| Engine | Adapter | Status |
| --- | --- | --- |
| INFINI Reference | built-in | ready |
| Hermes | `adapters/hermes/` | ready |
| OpenClaw | `adapters/openclaw/` | ready |
| LangGraph | community | planned |

## Metrics

For each engine, report:

| Metric | Definition |
| --- | --- |
| Runtime (mean, p50, p95) | Wall-clock from `infini run` to outcome. |
| Cost (mean, p95) | Dollar cost per run. |
| Tokens (mean) | Total tokens consumed. |
| Verification rate | Fraction of runs that shipped `verified`. |
| Failure modes | Categorized: budget_exceeded, unverified, error. |
| Replay fidelity | Bit-exact with `--freeze-model-calls`? |

## Results

_Populated once the benchmark harness runs. See `benchmarks/reports/`
for raw traces._

## Expected findings

We expect:

- **INFINI Reference** will be the slowest (it's the reference impl, not
  optimized for speed).
- **Hermes** will have governance overhead (policy checks, audit
  signing) that adds latency but improves auditability.
- **OpenClaw** will be fastest on tool-heavy steps (browser, terminal)
  due to its tool-calling optimization.
- **Verification rate** should be similar across engines — verification
  is a property of the loop, not the engine.

If the results don't match these expectations, that's interesting data.
We publish whatever we find.

## Cross-engine diff

```bash
infini diff runs/infini/latest/ runs/hermes/latest/
infini diff runs/hermes/latest/ runs/openclaw/latest/
```

The diff shows where engines diverge: which steps took longer, which
cost more, which produced different artifacts.

## Reproducing

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini benchmark benchmarks/fixtures/coding-loop/ --engine infini --n 10
infini benchmark benchmarks/fixtures/coding-loop/ --engine hermes --n 10
infini benchmark benchmarks/fixtures/coding-loop/ --engine openclaw --n 10
```

Attach your `run.json` traces to a PR to `benchmarks/reports/`.
