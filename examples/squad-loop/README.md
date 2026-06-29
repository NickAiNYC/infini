# Squad Collaboration Loop

> Declarative mapping of a multi-agent handoff pattern.
> Write spec → expand → implement → verify.

## What this demonstrates

- **Sequential agent pipeline** (plan → research → implement → verify)
- **Prompt-driven agents** (each agent has a typed role and instruction)
- **Command escape hatch** (s5 uses `command:` for exit-code logic)
- **Full verification** (syntactic `:exists` / `:contains` + semantic quality thresholds)
- **Budget enforcement** ($5 cap, 10-minute wall clock)

## The pattern

```
spec ──→ planner ──→ plan.md
         expander ──→ research.md
         implementer ─→ src/ + tests/ + README
         verifier   ──→ verify-report.json
         shell      ──→ final exit check
```

This maps a typical Squad CLI session — plan with a reasoning model,
expand with a fast model, implement with a code model, verify with a
lightweight judge — into a declarative, portable Loopfile.

## Run it

```bash
infini validate examples/squad-loop/Loopfile.yaml
infini run examples/squad-loop/Loopfile.yaml --live

# Compare traces against Squad's imperative output
infini diff runs/squad-impure/ runs/squad-loop/
# → Identical artifacts. Portable workflow.
```

## Why declarative beats imperative

| Dimension | Squad CLI (imperative) | INFINI Loopfile (declarative) |
|-----------|----------------------|-------------------------------|
| Definition | Manual CLI commands | YAML spec |
| Reproducibility | Copy-paste | `infini run` |
| Verification | Trust | `:exists`, `:contains`, `quality>=80` |
| Trace | None | Full JSON |
| Replay | None | `infini replay` from any step |
| Budget | None | `BUDGET: { dollars: 5 }` |
| Portability | Squad-specific | Any conforming engine |

## Conceptual mapping: Squad → INFINI

| Squad concept | INFINI equivalent |
|---------------|-------------------|
| Declare a role | `AGENTS[]` with `role:` + `prompt:` |
| Assign a model | `model_tier:` (engine-resolved) |
| Hand off between agents | `STEPS[]` with `depends_on:` |
| Pass artifacts | `produces:` |
| Check work | `VERIFY` block + `STOP_WHEN: ["all_verify_passed"]` |

## Related

- [Squad CLI](https://github.com/tom-doerr/squad_cli) — the imperative original
- [Multi-agent orchestration](../multi-agent-orchestration/) — parallel fan-out pattern

## Validation note

This example requires the local development schema included in this repository.
The `prompt`, `command`, and `memory.artifacts` fields were added to the spec
for this pattern and are not yet in the Homebrew-distributed schema.

If `infini validate` fails from a Homebrew-installed CLI, reinstall from source:

```bash
pip install -e './cli[dev]'
infini validate examples/squad-loop/Loopfile.yaml
```
