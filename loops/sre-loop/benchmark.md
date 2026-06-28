# Benchmark — sre-loop

Sample benchmark for `sre-loop` on the INFINI Reference Engine.

> This is a representative benchmark, not a guarantee. Your numbers will
> vary based on model tier, prompt, and inputs. Run
> [`infini benchmark`](../../cli/README.md) on your own infrastructure
> for real numbers.

## Result

| Metric | Value |
| --- | --- |
| Iterations | 3 |
| Runtime | 12.80 minutes |
| Cost | $3.94 |
| Verification | passed (confidence 88) |
| Failures | 0 |
| Artifacts | 5 |
| Replay fidelity | bit-exact with `--freeze-model-calls` |

## Inputs

- Engine: INFINI Reference Engine 1.0.0
- Model tier: sonnet (builder), haiku (verifier)
- Spec version: LOOPFILE-1.0

## Compare across engines

```bash
infini benchmark loops/sre-loop/Loopfile.yaml --engine hermes
infini benchmark loops/sre-loop/Loopfile.yaml --engine openclaw
infini benchmark loops/sre-loop/Loopfile.yaml --engine infini
infini diff runs/hermes/latest/ runs/openclaw/latest/
```

See [`benchmarks/`](../../benchmarks/) for cross-engine comparisons.
