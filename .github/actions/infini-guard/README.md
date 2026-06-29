# INFINI Guard — GitHub Action

Audit your agent project for loop portability on every PR.

## What it does

- Runs `infini audit` on your project directory
- Runs `infini validate` on every `Loopfile.yaml`
- Fails the build if the audit score drops below your threshold (default: 50 = L2 Assisted)
- Fails if any Loopfile is invalid

## Quick start

Add this to `.github/workflows/infini-guard.yml` in your repo:

```yaml
name: INFINI Guard
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: NickAiNYC/infini/.github/actions/infini-guard@main
        with:
          project-dir: '.'
          min-score: '50'
```

That's it. The action installs INFINI automatically. No Python setup needed.

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `project-dir` | `.` | Directory to audit (relative to repo root) |
| `min-score` | `50` | Minimum audit score (0-100) to pass. 50 = L2 Assisted, 75 = L3 Unattended |
| `fail-on-validate` | `true` | Fail the build if any Loopfile.yaml fails validation |

## Example output

On a passing PR:

```
✓ Audit score: 55 / 100 (L2 Assisted)
✓ All Loopfiles valid
```

On a failing PR:

```
✗ INFINI audit score 26 is below minimum 50 (L1 Report-only)
✗ Run 'infini audit .' locally to see missing signals and fixes
```

## Maturity levels

| Level | Score | Meaning |
|-------|-------|---------|
| L0 Draft | 0-24 | Aspirational, no infrastructure |
| L1 Report-only | 25-49 | Runs but produces no durable artifacts |
| L2 Assisted | 50-74 | Has state, verification, and replay |
| L3 Unattended | 75-100 | Production-ready with CI + safety |

Set `min-score: '75'` if you want to enforce L3 Unattended on your production loops.
