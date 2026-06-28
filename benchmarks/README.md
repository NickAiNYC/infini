# INFINI Benchmarks

> Benchmarks for canonical loops across engines. Every benchmark includes
> the raw `run.json` traces so others can verify. No fake numbers.

## Benchmark suite

| Benchmark | What it tests |
| --- | --- |
| [`browser-automation`](browser-automation/) | Navigate, scrape, verify across web pages. |
| [`coding`](coding/) | Implement feature, preserve tests, open PR. |
| [`research`](research/) | Multi-source research with citations. |
| [`planning`](planning/) | Break down complex task into executable plan. |
| [`refactoring`](refactoring/) | Refactor without behavior change. |
| [`compliance`](compliance/) | Audit claims with escalation. |
| [`hybrid-agent`](hybrid-agent/) | Hermes + OpenClaw on same Loopfile. |
| [`cost-optimization`](cost-optimization/) | Complete task within tight budget. |

## How to run a benchmark

```bash
infini run benchmarks/coding/Loopfile.yaml --mock
infini inspect runs/latest/
```

## Methodology

- **N = 10 runs** per engine per loop, unless stated otherwise.
- **Same inputs** across engines.
- **Same model tier** across engines, where supported.
- **No cherry-picking.** All runs reported, including failures.
- **Replay fidelity** measured with `--freeze-model-calls`.

## Reporting

To publish a benchmark result:

1. Run the benchmark with `infini run --mock -o runs/<id>/`.
2. Write a markdown report in `benchmarks/reports/<date>-<loop>-<engine>.md`.
3. Attach the raw `run.json` traces.
4. PR to `benchmarks/reports/`.

## What benchmarks are not

- Not a leaderboard. We report numbers; you decide.
- Not a model benchmark. INFINI is model-agnostic.
- Not a marketing tool. Honest data only.
