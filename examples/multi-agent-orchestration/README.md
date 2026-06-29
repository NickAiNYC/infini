# Multi-Agent Orchestration — Golden Example

> Parallel fan-out + fan-in. Three workers + merge + verify.

## What this demonstrates

- **DAG parallelism** (3 workers execute concurrently after input step)
- **Fan-out / fan-in** pattern
- **3-agent supervision** when run with `--plan`
- **Cross-verification** (merge quality checked by separate verifier)

## Run it

```bash
# Standard execution
infini validate examples/multi-agent-orchestration/Loopfile.yaml
infini run examples/multi-agent-orchestration/Loopfile.yaml --mock

# With 3-agent orchestration (Planner/Worker/Inspector)
infini run examples/multi-agent-orchestration/Loopfile.yaml --plan

# Inspect the trace
infini inspect runs/latest/
```

## Loop flow

```
         ┌── worker_a ──┐
input ───┼── worker_b ──┼── merge ── verify
         └── worker_c ──┘
```
