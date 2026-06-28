# Benchmark: Browser Loop

Loop: `infini/browser-agent-loop@1.0` (OpenClaw adapter)
Engines: OpenClaw
Last run: planned

> This benchmark spec is final; the numbers are not yet populated. Once
> the adapters ship, this file will be updated with real results.

---

## Loop

See [`adapters/openclaw/examples/browser-agent-loop.yaml`](../adapters/openclaw/examples/browser-agent-loop.yaml) for the loop definition.

## Inputs

10 browser tasks (scrape pricing page, fill form, navigate multi-page flow).

Fixtures live in `benchmarks/fixtures/browser-agent-loop/` (planned).

## Engines

Each engine runs all fixtures, 10 times each (N=10 per fixture per engine).

## Metrics

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

OpenClaw is the only engine with browser tools today. This benchmark establishes the baseline. When other engines add browser support, they'll be added to this benchmark.

If the results don't match these expectations, that's interesting data.
We publish whatever we find.

## Reproducing

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini benchmark benchmarks/fixtures/browser-agent-loop/ --engine infini --n 10
```

Attach your `run.json` traces to a PR to `benchmarks/reports/`.
