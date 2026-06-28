# Benchmark — debug-loop

Sample benchmark for `debug-loop` on the INFINI Reference Engine.

> This is a representative benchmark, not a guarantee. Your numbers will
> vary based on model tier, prompt, and inputs. Run
> [`infini benchmark`](../../cli/README.md) on your own infrastructure
> for real numbers.

## Result

| Metric | Value |
| --- | --- |
| Iterations | 3 |
| Runtime | 8.40 minutes |
| Cost | $2.34 |
| Verification | passed (confidence 88) |
| Failures | 0 |
| Artifacts | 4 |
| Replay fidelity | bit-exact with `--freeze-model-calls` |

## Inputs

- Engine: INFINI Reference Engine 1.0.0
- Model tier: sonnet (builder), haiku (verifier)
- Spec version: LOOPFILE-1.0

## Compare across engines

```bash
infini benchmark loops/debug-loop/Loopfile.yaml --engine hermes
infini benchmark loops/debug-loop/Loopfile.yaml --engine openclaw
infini benchmark loops/debug-loop/Loopfile.yaml --engine infini
infini diff runs/hermes/latest/ runs/openclaw/latest/
```

See [`benchmarks/`](../../benchmarks/) for cross-engine comparisons.
