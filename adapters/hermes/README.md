# INFINI × Hermes Adapter

> **Hermes is the governed operating system.** This adapter lets any Loopfile run as a governed Hermes operation — with memory, audit trails, budget policy, and escalation.

INFINI is not another agent framework. INFINI is the **portable loop standard** that sits above runtimes. Hermes handles governance; this adapter translates a Loopfile into a governed Hermes operation.

Use this adapter when you need:

- **policy** — declare what the loop may and may not do
- **memory** — let the loop remember across runs
- **escalation** — hand off to a human when confidence drops or budget is hit
- **audit trails** — every decision, every token, every artifact, signed
- **business-objective alignment** — tie loop outcomes to org objectives

For pure execution (browser actions, repo edits, terminal commands), use the [OpenClaw adapter](../openclaw/) instead. For combined governance + execution, see the [hybrid demo](../../examples/hybrid-hermes-openclaw/).

---

## Architecture

```text
Loopfile
  ↓
INFINI Parser + Validator
  ↓
Hermes Adapter              ← you are here
  ↓
Hermes governed operation
  ↓
Trace + Verification + Replay
```

The Hermes adapter is responsible for translating Loopfile primitives (`AGENTS`, `STEPS`, `VERIFY`, `BUDGET`) into Hermes governance primitives. It does not itself execute agent actions; it routes execution to either a Hermes-native agent or, in hybrid mode, to the OpenClaw adapter.

---

## Install

```bash
pip install infini-cli[hermes]
```

The adapter is bundled with the INFINI CLI but registered only when the `hermes` extra is installed.

---

## Configure

A Loopfile declares its engine via the `ENGINE` block:

```yaml
ENGINE:
  type: hermes
  adapter: adapters/hermes
  governance:
    memory: true
    audit_log: true
    budget_policy: strict       # strict | advisory | off
    escalation_policy: enabled  # enabled | disabled
```

| Field                  | Values                 | Meaning |
| ---------------------- | ---------------------- | ------- |
| `type`                 | `hermes`               | Selects this adapter. |
| `adapter`              | `adapters/hermes`      | Adapter module path. |
| `governance.memory`    | bool                   | Persist lessons and decisions across runs. |
| `governance.audit_log` | bool                   | Sign every step's trace entry. |
| `governance.budget_policy` | `strict` \| `advisory` \| `off` | In `strict`, exceeding budget aborts the run. In `advisory`, it warns. `off` disables enforcement. |
| `governance.escalation_policy` | `enabled` \| `disabled` | If enabled, the loop pauses and notifies a human when confidence drops below threshold or a verifier fails twice in a row. |

See [`adapter.yaml`](adapter.yaml) for the adapter's own manifest.

---

## Use Hermes for

- **policy** — declarative constraints on agent behavior
- **memory** — durable, queryable run history
- **escalation** — structured human-in-the-loop handoff
- **audit trails** — signed, append-only decision logs
- **business-objective alignment** — link loop outcomes to OKRs
- **agent governance** — who can run what, when, with what budget

---

## Examples

Three Loopfiles ship with this adapter:

| Loopfile | What it demonstrates |
| -------- | -------------------- |
| [`governed-growth-loop.yaml`](examples/governed-growth-loop.yaml) | A growth-marketing loop with strict budget policy and audit logging. |
| [`claim-audit-loop.yaml`](examples/claim-audit-loop.yaml) | An insurance-claims audit loop with escalation on low confidence. |
| [`recovery-loop.yaml`](examples/recovery-loop.yaml) | An incident-recovery loop with memory across incidents. |

Run any of them:

```bash
infini run adapters/hermes/examples/claim-audit-loop.yaml
```

---

## Conformance

This adapter implements:

| Capability       | Status |
| ---------------- | :----: |
| Parse Loopfile   |   ✅   |
| Run Loop         |   ✅   |
| Verify           |   ✅   |
| Inspect Trace    |   ✅   |
| Replay           |   ✅   |
| Diff             |   🚧   |

The full conformance row lives in [`spec/compatibility.md`](../../spec/compatibility.md).

---

## Governance hooks

The Hermes adapter emits governance-specific fields in the trace:

```json
{
  "governance": {
    "policy_violations": [],
    "escalations": [
      { "at_step": "s3", "reason": "confidence_below_threshold", "value": 71 }
    ],
    "audit_hash": "sha256:9f3a...",
    "memory_refs": ["incidents/2026-06-20#auth-service-down"]
  }
}
```

These are visible in the Loop Observatory under the **Governance** tab.

---

## License

MIT. See [repository LICENSE](../../LICENSE).
