# Governance

Chapter 8 of the [INFINI Handbook](README.md).

> Loops you can't govern are loops you can't ship in production.

---

## Why governance

A loop that runs without oversight is a loop that can do damage. It can
edit the wrong file, send the wrong email, deploy the wrong code.
Governance is the discipline of making loops safe to ship.

Governance is not the same as verification. Verification asks "did the
loop produce correct output?" Governance asks "was the loop allowed to
produce this output in the first place?" Both are required.

---

## What governance adds

The Hermes adapter adds four things on top of the basic Loopfile model:

### 1. Policy

```yaml
ENGINE:
  type: hermes
  governance:
    budget_policy: strict
    escalation_policy: enabled
```

Policy declares what the loop may and may not do. `budget_policy: strict`
means exceeding the budget aborts the run. `escalation_policy: enabled`
means the loop pauses and notifies a human when confidence drops.

Policy is enforced by the adapter, not by the loop. The loop can't opt
out of policy; the loop's author can't weaken it.

### 2. Memory

Hermes persists memory across runs. A loop that runs today can recall
what it learned last week. This is the `LESSONS` block from
[Chapter 5](memory.md), but Hermes makes it durable and queryable.

### 3. Escalation

```text
▶ s3 decide                     ⚠  confidence 71 < 80, escalating
▶   ↳ notified reviewer: ops-oncall
▶ s3 decide (after review)      ✓  $0.83  ·  2m34s
```

When a verifier fails twice in a row, or confidence drops below
threshold, Hermes pauses the loop and notifies a human. The human
reviews, decides, and the loop resumes.

This is the human-in-the-loop pattern. It's how you ship loops in
high-stakes domains (compliance, healthcare, finance) where being wrong
is expensive.

### 4. Audit trails

Every Hermes run produces a signed audit log. Every decision, every
token, every artifact is recorded. The log is append-only and signed by
the adapter's key. It's evidence, not just a log.

This is what makes loops shippable in regulated industries. Auditors
don't trust models; they trust audit trails. Hermes produces audit
trails.

---

## The hybrid pattern

The most powerful pattern in INFINI is the hybrid: Hermes governs,
OpenClaw executes, INFINI records and replays.

```text
Loopfile → Hermes policy/memory/governance → OpenClaw execution/tools → INFINI trace/replay/verify
```

This separates the loop from the runtime. Hermes handles the governance
concerns (policy, memory, escalation, audit). OpenClaw handles the
execution concerns (tools, browser, repo, terminal). INFINI handles the
portability concerns (trace, replay, verify, diff).

The hybrid demo is at [`examples/hybrid-hermes-openclaw/`](../../examples/hybrid-hermes-openclaw/).
It's the market hook for INFINI — the missing protocol between governance
systems and agent runtimes.

---

## When to govern

Not every loop needs governance. A `coding-loop` that opens a PR on a
feature branch doesn't need policy or escalation — the PR review *is* the
governance.

Governance is for loops where:

- **The action is irreversible.** Sending an email, deploying to
  production, paying an invoice. You can't undo these; you need to
  approve before they happen.
- **The domain is regulated.** Compliance, healthcare, finance. Auditors
  require evidence; Hermes produces it.
- **The cost of being wrong is high.** A wrong coding-loop PR wastes 20
  minutes of review time. A wrong compliance-loop decision costs the
  company money. Govern the latter; don't govern the former.
- **The loop runs unattended.** If a loop runs in CI, on a schedule, or
  in response to an event, no human is watching. Governance is the
  substitute for watching.

---

## When NOT to govern

Governance has cost. It adds latency (policy checks), complexity (audit
signing), and friction (escalation pauses). Don't add it where it's not
needed.

A `coding-loop` that runs in a feature branch and opens a PR does not
need Hermes. The PR review process is the governance. Adding Hermes on
top would double-govern and slow the loop down.

A `debug-loop` that runs interactively (a developer is watching) does not
need escalation. The developer *is* the escalation.

Governance is for unattended, irreversible, regulated, or high-stakes
loops. For everything else, the Loopfile's `VERIFY` block is sufficient.

---

## The audit trail as evidence

The Hermes audit log is signed and append-only. This makes it evidence,
not just a log. In regulated industries, this is the difference between
"we have a log" and "we have a defensible record."

The audit log includes:

- Every step's start and end time.
- Every step's cost (tokens, dollars, minutes).
- Every verifier's result, including confidence.
- Every policy decision (allowed / denied / escalated).
- Every artifact produced, with its content hash.
- Every escalation, with the reason and the reviewer.

This is what auditors want. Not "the model said it was fine" — "here is
the signed record of every decision the loop made."

---

## What's next

- Chapter 9, [Portability](portability.md) — loops that survive engine swaps.
- For the Hermes adapter, see [`adapters/hermes/`](../../adapters/hermes/).
- For the hybrid demo, see [`examples/hybrid-hermes-openclaw/`](../../examples/hybrid-hermes-openclaw/).
