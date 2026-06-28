# Benchmark: Hybrid Loop

Loop: `infini/governed-coding-loop@1.0` (Hermes + OpenClaw)
Engines: Hybrid (Hermes governance + OpenClaw execution)
Last run: planned

> This benchmark spec is final; the numbers are not yet populated. Once
> the adapters ship, this file will be updated with real results.

---

## Loop

See [`examples/hybrid-hermes-openclaw/`](../examples/hybrid-hermes-openclaw/) for the loop definition.

## Inputs

10 coding tasks that require governance (touch production code, open PRs to main).

Fixtures live in `benchmarks/fixtures/hybrid-loop/` (planned).

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

Hybrid mode adds governance overhead (policy_check, audit_pre, audit_post) but produces a signed audit trail. The benchmark quantifies the overhead: how much extra cost and latency does governance add, and is the audit trail worth it?

If the results don't match these expectations, that's interesting data.
We publish whatever we find.

## Reproducing

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini benchmark benchmarks/fixtures/hybrid-loop/ --engine infini --n 10
```

Attach your `run.json` traces to a PR to `benchmarks/reports/`.
