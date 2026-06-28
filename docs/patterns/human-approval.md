# Human Approval Pattern

## Problem

A step produces an irreversible action: sending an email, deploying to
production, paying an invoice. You need a human to approve before the
action happens.

## Diagram

```text
prepare → [HUMAN APPROVAL] → execute → verify
```

## Loopfile

```yaml
STEPS:
  - id: s3
    name: prepare_send
    action: email.prepare
    uses: builder
    produces: [email-draft.json]
  - id: s4
    name: human_approval
    action: governance.await_approval
    uses: auditor
    depends_on: [s3]
    produces: [approval.json]
  - id: s5
    name: send
    action: email.send
    uses: builder
    depends_on: [s4]
    produces: [sent-email.json]

STOP_WHEN:
  - all_verify_passed
  - "predicate:approval_denied"   # stop if the human says no
```

## Tradeoffs

**Gives:**
- Safety on irreversible actions.
- Audit trail of who approved what and when.

**Costs:**
- The loop pauses. Latency goes from minutes to hours (or days).
- A human has to actually review. If they rubber-stamp, the pattern is
  theater.

## Best practices

- **Approve the artifact, not the step.** The human reviews
  `email-draft.json`, not "step s4." Make the artifact the unit of
  approval.
- **Time-box the approval.** If the human doesn't respond in N hours,
  either escalate or abort. Don't let loops wait forever.
- **Record the approver.** `approval.json` should include who approved,
  when, and any comments. This is the audit trail.
- **Don't use this pattern for reversible actions.** PR review is
  reversible; you can revert a merge. Email is not; you can't unsend.
  Govern the latter; don't govern the former.
- **Pair with the [Escalation](escalation.md) pattern.** If approval is
  denied, escalate — don't silently fail.
