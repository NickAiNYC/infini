# INFINI Benchmarks

> Benchmarks for canonical loops across engines. Every benchmark includes
> the raw `run.json` traces so others can verify. No fake numbers.

Benchmarks answer four questions:

1. **How fast?** Wall-clock runtime.
2. **How much?** Dollar cost and token usage.
3. **How reliable?** Verification rate (what fraction of runs ship
   `verified`).
4. **How reproducible?** Replay fidelity (does `--freeze-model-calls`
   produce bit-exact traces?).

---

## Benchmark suite

| Benchmark | Loop | Engines | Last run |
| --- | --- | --- | --- |
| [`coding-loop-bench`](coding-loop.md) | `infini/coding-loop@1.0` | INFINI Reference, Hermes, OpenClaw | planned |
| [`research-loop-bench`](research-loop.md) | `infini/research-loop@1.0` | INFINI Reference, OpenClaw | planned |
| [`compliance-loop-bench`](compliance-loop.md) | `infini/claim-audit-loop@1.0` (Hermes) | Hermes-only vs. hybrid | planned |
| [`browser-loop-bench`](browser-loop.md) | `infini/browser-agent-loop@1.0` (OpenClaw) | OpenClaw | planned |
| [`hybrid-loop-bench`](hybrid-loop.md) | `infini/governed-coding-loop@1.0` | Hybrid (Hermes+OpenClaw) | planned |

---

## How to run a benchmark

```bash
infini benchmark loops/coding-loop/Loopfile.yaml --engine infini
infini benchmark loops/coding-loop/Loopfile.yaml --engine hermes
infini benchmark loops/coding-loop/Loopfile.yaml --engine openclaw

# Compare
infini diff runs/infini/latest/ runs/hermes/latest/
```

Each benchmark produces a `run.json` trace. The benchmark report
aggregates:

- Runtime (mean, p50, p95) across N runs.
- Cost (mean, p95).
- Verification rate (what fraction of runs shipped `verified`).
- Failure modes (why did the others fail?).
- Replay fidelity (bit-exact vs. model-drift).

---

## Reporting a benchmark

To publish a benchmark result:

1. Run the benchmark with `infini benchmark --save runs/<id>/`.
2. Write a markdown report in `benchmarks/reports/<date>-<loop>-<engine>.md`.
3. Attach the raw `run.json` traces (or a link to them).
4. PR to `benchmarks/reports/`.

The report must include:

- Engine name and version.
- Model tier used.
- Inputs (or a pointer to them, if too large to commit).
- The four metrics above.
- Any anomalies (high variance, unexpected failures).

---

## Methodology

- **N = 10 runs** per engine per loop, unless stated otherwise.
- **Same inputs** across engines. The benchmark harness fixes the inputs;
  only the engine varies.
- **Same model tier** across engines, where the engine supports it. Where
  it doesn't, the report notes the difference.
- **No cherry-picking.** All N runs are reported, including failures. The
  verification rate is the fraction that shipped `verified`, not the
  fraction that were "good enough."
- **Replay fidelity** is measured with `--freeze-model-calls`. A
  bit-exact replay means the engine's state model is sound.

---

## What benchmarks are not

- **Not a leaderboard.** We don't rank engines. We report numbers; you
  decide.
- **Not a model benchmark.** INFINI is model-agnostic. Model
  comparisons happen at the engine level, not the loop level.
- **Not a marketing tool.** A benchmark that makes INFINI look bad is
  still published. The point is honest data.

---

## License

CC-BY-4.0 for the benchmark specs. MIT for the harness code. See
[repository LICENSE](../LICENSE).
