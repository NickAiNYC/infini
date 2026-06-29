# Claim Audit

> **Governance brain: policy, budget, escalation, audit trail.**
>
> Run a claim-audit loop with policy, budget, escalation, and audit trail.

This is the **governance brain** demo. For pure execution, see [GitHub PR Review](../github-pr-review/). For both together, see [Hybrid (deprecated)](../_deprecated/hybrid-hermes-openclaw/).

---

## What this demo shows

- **Policy enforcement.** The loop refuses to ship a decision that doesn't cite policy.
- **Budget enforcement.** The loop aborts if `BUDGET` is exceeded.
- **Escalation.** When semantic confidence drops below threshold, the loop pauses and notifies a human reviewer.
- **Audit trail.** Every step is signed; the audit log is append-only.
- **Memory.** Prior claim decisions are recalled to inform the current one.

This is the **governance brain** demo. For pure execution, see [GitHub PR Review](../github-pr-review/). For both together, see [Hybrid (deprecated)](../_deprecated/hybrid-hermes-openclaw/).

---

## Architecture

```text
Loopfile (claim-audit-loop.yaml)
  ↓
INFINI Parser + Validator
  ↓
Hermes Adapter
  ↓
Hermes governed operation
  ├─ policy.cross_check
  ├─ claims.decide
  └─ audit.sign
  ↓
Trace + Verification + Replay (in INFINI)
```

---

## Run it

```bash
# From the repo root
infini run examples/claim-audit/claim-audit-loop.yaml

# Inspect the trace
infini inspect runs/latest/

# Replay from the decision step
infini replay runs/latest/ --step s3
```

> The Loopfile in this folder is a thin wrapper around
> [`adapters/hermes/examples/claim-audit-loop.yaml`](../../adapters/hermes/examples/claim-audit-loop.yaml),
> pinned to a specific version so the demo is reproducible.

---

## What you'll see

```text
$ infini run examples/claim-audit/claim-audit-loop.yaml
▶ engine: hermes
▶ governance: memory=on audit=on budget=strict escalation=on
▶ reading state... none found, starting fresh
▶ s1 gather_evidence            ✓  $0.42  ·  1m12s
▶ s2 cross_check_policy         ✓  $0.61  ·  1m48s
▶ s3 decide                     ⚠  confidence 71 < 80, escalating
▶   ↳ notified reviewer: ops-oncall
▶ s3 decide (after review)      ✓  $0.83  ·  2m34s
▶ s4 audit_sign                 ✓  $0.22  ·  0m21s
▶ verification: cite_policy PASS · evidence_quality 86 PASS
▶ cost: $2.08 / $4.00 · 6m55s / 12m
✓ shipped. state saved. lessons appended. audit hash: sha256:9f3a…
```

The `⚠` line is the escalation. The audit hash at the end is signed by Hermes and visible in the Loop Observatory's Governance tab.

---

## Files

- `claim-audit-loop.yaml` — the runnable demo Loopfile
- `expected-output.md` — what a successful run looks like (for CI)
- `README.md` — this file

---

## Takeaway

Governance is a property of the loop, not a property of the runtime. Write the governance once in the Loopfile; Hermes enforces it; INFINI records it. Swap engines later without losing the audit trail.
