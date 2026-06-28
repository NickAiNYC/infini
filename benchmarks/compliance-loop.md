# Benchmark: Compliance Loop

Loop: `infini/claim-audit-loop@1.0` (Hermes adapter)
Engines: Hermes-only vs. Hybrid (Hermes + OpenClaw)
Last run: planned

> This benchmark spec is final; the numbers are not yet populated. Once
> the adapters ship, this file will be updated with real results.

---

## Loop

See [`adapters/hermes/examples/claim-audit-loop.yaml`](../adapters/hermes/examples/claim-audit-loop.yaml) for the loop definition.

## Inputs

10 insurance claims of varying complexity (simple approve, complex deny, edge-case escalate).

Fixtures live in `benchmarks/fixtures/claim-audit-loop/` (planned).

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

Hermes-only will be faster (no execution delegation overhead). Hybrid will produce richer traces (governance + tools). Verification rate should be identical; audit trail should be present in both.

If the results don't match these expectations, that's interesting data.
We publish whatever we find.

## Reproducing

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini benchmark benchmarks/fixtures/claim-audit-loop/ --engine infini --n 10
```

Attach your `run.json` traces to a PR to `benchmarks/reports/`.
