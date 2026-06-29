# Demo: Hybrid (Hermes governs, OpenClaw executes, INFINI records)

> **This is the market hook.**
>
> Hermes governs. OpenClaw executes. INFINI records and replays.

This demo runs a single Loopfile that combines Hermes governance with OpenClaw execution. The same Loopfile is portable: you can run it governance-only, execution-only, or both together — without changing the loop's definition.

This is the demo that makes INFINI look like the missing protocol between governance systems and agent runtimes.

---

## What this demo shows

- **One Loopfile, two adapters.** A `governed-coding-loop` that runs a coding task under Hermes governance and OpenClaw execution.
- **Policy before action.** Hermes checks the plan against policy *before* OpenClaw edits files.
- **Audit + tools in one trace.** The same `run.json` carries both `governance.audit_hash` and `tools.calls`.
- **Replay across the boundary.** You can replay from any step — Hermes-side or OpenClaw-side — and the other side picks up correctly.

If you only run one demo, run this one.

---

## Architecture

```text
Loopfile (governed-coding-loop.yaml)
  ↓
INFINI Parser + Validator
  ↓
┌──────────────────────────┐
│ Hermes Adapter           │   ← governance brain
│  • policy.cross_check    │
│  • audit.sign            │
│  • escalation (if needed)│
└──────────────────────────┘
  ↓ delegates execution to
┌──────────────────────────┐
│ OpenClaw Adapter         │   ← execution runtime
│  • file_system.write     │
│  • terminal.run          │
│  • github.open_pr        │
└──────────────────────────┘
  ↓
Trace + Verification + Replay (in INFINI)
```

The Hermes adapter is the **governance brain**: policy, memory, escalation, audit trails. The OpenClaw adapter is the **execution runtime**: tools, browser, repo edits, terminal. INFINI is the **portable loop standard** that sits above both.

---

## Run it

```bash
# From the repo root
infini run examples/hybrid-hermes-openclaw/governed-coding-loop.yaml

# Inspect the trace — note both governance and tools tabs are populated
infini inspect runs/latest/

# Replay from the Hermes policy-check step
infini replay runs/latest/ --step s2

# Replay from the OpenClaw edit step
infini replay runs/latest/ --step s4
```

> The Loopfile in this folder is original to this demo. It is not a copy
> of an adapter example — it is the canonical demonstration of hybrid mode.

---

## What you'll see

```text
$ infini run examples/hybrid-hermes-openclaw/governed-coding-loop.yaml
▶ engine: hermes (governance) + openclaw (execution)
▶ governance: memory=on audit=on budget=strict escalation=on
▶ tools: file_system, terminal, github
▶ reading state... none found, starting fresh

▶ s1 plan                       ✓  $0.18  ·  0m42s   [hermes: planner]
▶ s2 policy_check               ✓  $0.31  ·  0m54s   [hermes: auditor] policy: PASS
▶ s3 audit_pre                  ✓  $0.12  ·  0m18s   [hermes: audit.sign]
▶ ── delegating to openclaw ──
▶ s4 edit_files                 ✓  $0.34  ·  1m12s   [openclaw] tools: file_system.write ×2
▶ s5 run_tests                  ✓  $0.21  ·  0m48s   [openclaw] tools: terminal.run ×1, exit 0
▶ s6 open_pr                    ✓  $0.22  ·  0m36s   [openclaw] tools: github.open_pr → PR #4130
▶ ── returning to hermes ──
▶ s7 audit_post                 ✓  $0.14  ·  0m21s   [hermes: audit.sign] hash: sha256:b7c1…
▶ s8 verify_governed            ✓  $0.18  ·  0m30s   [hermes: auditor] confidence 91

▶ verification: tests:pass PASS · completeness 92 PASS · policy_citation 95 PASS
▶ cost: $1.70 / $6.00 · 4m21s / 18m
✓ shipped. state saved. lessons appended. audit hash: sha256:b7c1…
✓ PR: https://github.com/org/repo/pull/4130
```

The `── delegating to openclaw ──` and `── returning to hermes ──` lines are how you see the handoff in the terminal. In the Loop Observatory, the same handoff is shown as a swimlane view: Hermes lane and OpenClaw lane, with the delegation arrows between them.

---

## The `ENGINE` block (hybrid mode)

```yaml
ENGINE:
  type: hermes                  # primary engine: governance
  adapter: adapters/hermes
  governance:
    memory: true
    audit_log: true
    budget_policy: strict
    escalation_policy: enabled
  delegates:
    execution:                  # hand execution to OpenClaw
      type: openclaw
      adapter: adapters/openclaw
      tools: [file_system, terminal, github]
```

The primary engine is `hermes`. The `delegates.execution` block tells the Hermes adapter to route any step whose `uses` agent is OpenClaw-resolved to the OpenClaw adapter. Both adapters write to the same `run.json`.

---

## Files

- `governed-coding-loop.yaml` — the runnable hybrid demo Loopfile
- `expected-output.md` — what a successful run looks like (for CI)
- `README.md` — this file

---

## Takeaway

This is the missing protocol. Governance systems and agent runtimes have been hard-coupled because no portable loop format existed between them. INFINI is that format. Write one Loopfile. Govern with Hermes. Execute with OpenClaw. Keep the same verification, trace, budget, and replay model across both.

Swap Hermes for another governance system later. Swap OpenClaw for another runtime later. The Loopfile doesn't change.
