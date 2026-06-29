# Canonical Supervisor Loop

> The universal supervision pattern: Planner → Worker → Inspector.
> Runs on both the INFINI reference engine and LangGraph — same Loopfile, same outcome.

## Run it

```bash
# Reference engine
infini run loops/canonical-supervisor/loop.yaml --mock --engine infini

# LangGraph
infini run loops/canonical-supervisor/loop.yaml --mock --engine langgraph

# Diff the traces
infini diff runs/latest/run.json runs/langgraph/run.json
```

## Architecture

```
Planner → plan.md + task-breakdown.json
    ↓
Worker → execution-log.json + output.md
    ↓
Inspector → inspection-report.json
    ↓
VERIFY: 5 syntactic + 3 semantic (threshold: 85)
```
