# Canonical Corpus

> INFINI's "ImageNet for agent loops." Every engine should run these.
> Every release should run these. The corpus is durable.

## Cases

| # | Name | Category | Required capabilities |
| --- | --- | --- | --- |
| 001 | [`001-simple-task`](001-simple-task/) | minimal, baseline | `parse_loopfile`, `run_loop` |
| 002 | [`002-research-summary`](002-research-summary/) | research, verification | `parse_loopfile`, `run_loop`, `verify` |
| 003 | [`003-code-review`](003-code-review/) | coding, parallel, verification | `parse_loopfile`, `run_loop`, `verify` |
| 004 | [`004-retry-recovery`](004-retry-recovery/) | resilience, retry | `parse_loopfile`, `run_loop` |
| 005 | [`005-budget-guard`](005-budget-guard/) | budget, safety | `parse_loopfile`, `run_loop`, `budget` |
| 006 | [`006-parallel-fanout`](006-parallel-fanout/) | parallel, dag | `parse_loopfile`, `run_loop`, `dag_parallel` |
| 007 | [`007-memory-update`](007-memory-update/) | memory, learning | `parse_loopfile`, `run_loop`, `memory` |
| 008 | [`008-tool-call-placeholder`](008-tool-call-placeholder/) | tools, mcp | `parse_loopfile`, `run_loop`, `tools_mcp` |
| 009 | [`009-human-approval-gate`](009-human-approval-gate/) | governance, human-in-loop | `parse_loopfile`, `run_loop`, `verify` |
| 010 | [`010-replay-diff`](010-replay-diff/) | replay, diff, debugging | `parse_loopfile`, `run_loop`, `replay`, `diff` |

## Running the corpus

```bash
# Validate all corpus cases
for f in tests/corpus/*/Loopfile.yaml; do infini validate "$f"; done

# Run all corpus cases in mock mode
for f in tests/corpus/*/Loopfile.yaml; do infini run "$f" --mock; done
```

## Adding a case

1. Create `tests/corpus/<NNN>-<name>/`
2. Add `Loopfile.yaml`, `expected.json`, `README.md`
3. PR to `tests/corpus/`

Cases must be durable — once added, they do not change between releases
except to fix bugs. New cases are appended; existing case numbers are
never reused.
