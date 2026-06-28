# Benchmark: Research Loop

Loop: `infini/research-loop@1.0`
Engines: INFINI Reference, OpenClaw (browser tools required)
Last run: planned

> This benchmark spec is final; the numbers are not yet populated. Once
> the adapters ship, this file will be updated with real results.

---

## Loop

See [`loops/research-loop/`](../loops/research-loop/) for the loop definition.

## Inputs

10 research questions of varying difficulty (factual, analytical, multi-hop).

Fixtures live in `benchmarks/fixtures/research-loop/` (planned).

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

OpenClaw will be faster on browser-heavy steps; INFINI Reference will have more consistent citation verification. Verification rate (every_claim_has_citation) should be 100% across engines — the check is deterministic.

If the results don't match these expectations, that's interesting data.
We publish whatever we find.

## Reproducing

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini benchmark benchmarks/fixtures/research-loop/ --engine infini --n 10
```

Attach your `run.json` traces to a PR to `benchmarks/reports/`.
