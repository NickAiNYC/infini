# GitHub PR Review

> **Execution runtime: file edits, tests, PR creation.**
>
> Run a coding loop that edits files, runs tests, verifies output, and opens a PR.

This is the **execution runtime** demo. For governance, see [Claim Audit](../claim-audit/). For both together, see [Hybrid (deprecated)](../_deprecated/hybrid-hermes-openclaw/).

---

## What this demo shows

- **Tool execution.** OpenClaw agents call `file_system.write`, `terminal.run`, and `github.open_pr`.
- **Deterministic verification.** Tests must pass; the PR URL must be valid.
- **Semantic verification.** A judge agent scores feature completeness and test coverage.
- **Replay.** If a test fails, INFINI replays from the failing step with the same inputs.

This is the **execution runtime** demo. For governance, see [Claim Audit](../claim-audit/). For both together, see [Hybrid (deprecated)](../_deprecated/hybrid-hermes-openclaw/).

---

## Architecture

```text
Loopfile (coding-loop.yaml)
  ↓
INFINI Parser + Validator
  ↓
OpenClaw Adapter
  ↓
OpenClaw agents + tools
  ├─ file_system.write
  ├─ terminal.run (pytest)
  └─ github.open_pr
  ↓
Trace + Verification + Replay (in INFINI)
```

---

## Run it

```bash
# From the repo root
infini run examples/github-pr-review/coding-loop.yaml

# Inspect the trace
infini inspect runs/latest/

# Replay from the test step (e.g., to inspect why a test failed)
infini replay runs/latest/ --step s3
```

> The Loopfile in this folder is a thin wrapper around
> [`adapters/openclaw/examples/coding-loop.yaml`](../../adapters/openclaw/examples/coding-loop.yaml),
> pinned to a specific version so the demo is reproducible.

---

## What you'll see

```text
$ infini run examples/github-pr-review/coding-loop.yaml
▶ engine: openclaw
▶ tools: file_system, terminal, github
▶ reading state... none found, starting fresh
▶ s1 plan              ✓  $0.18  ·  0m42s
▶ s2 edit              ✓  $0.34  ·  1m12s   tools: file_system.write ×2
▶ s3 test              ✓  $0.21  ·  0m48s   tools: terminal.run ×1, exit 0
▶ s4 push_pr           ✓  $0.22  ·  0m36s   tools: github.open_pr → PR #4129
▶ verification: tests:pass PASS · completeness 92 PASS · coverage 87 PASS
▶ cost: $0.95 / $5.00 · 3m18s / 15m
✓ shipped. state saved. PR: https://github.com/org/repo/pull/4129
```

The `tools:` column is OpenClaw-specific. Every call — file write, terminal command, PR creation — is recorded in the trace and shown in the Loop Observatory's Tools tab.

---

## Files

- `coding-loop.yaml` — the runnable demo Loopfile
- `expected-output.md` — what a successful run looks like (for CI)
- `README.md` — this file

---

## Takeaway

Execution is a property of the loop, not a property of the runtime. Write the work once in the Loopfile; OpenClaw executes it; INFINI records it. Swap runtimes later without losing the trace.
