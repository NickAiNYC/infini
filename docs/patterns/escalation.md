# Escalation Pattern

## Problem

A loop's confidence drops below threshold, or a verifier fails twice in a
row. The loop should not silently fail, nor should it endlessly retry.
It should pause and notify a human.

## Diagram

```text
... → step → [CONFIDENCE < THRESHOLD?] → escalate → [HUMAN] → resume
                                         └─→ continue
```

## Loopfile

```yaml
ENGINE:
  type: hermes
  governance:
    escalation_policy: enabled

VERIFY:
  syntactic: [...]
  semantic:
    - "judge:correctness>=90"
  confidence_threshold: 90

STOP_WHEN:
  - all_verify_passed
  - "predicate:escalation_limit_reached"   # too many escalations → stop
```

The Hermes adapter fires an escalation when:
- A semantic check drops below threshold twice in a row.
- A syntactic check fails twice in a row.
- The budget reaches 80% of any ceiling.

## Tradeoffs

**Gives:**
- Human-in-the-loop safety on high-stakes loops.
- Audit trail of every escalation, with reason and reviewer.

**Costs:**
- The loop pauses. Latency goes from minutes to hours.
- If reviewers rubber-stamp, escalation is theater.

## Best practices

- **Escalate on evidence, not vibes.** The escalation must cite the
  specific check that failed and the confidence score. "The output feels
  off" is not an escalation trigger.
- **Notify the right human.** Different loops have different on-call
  rotations. The adapter should route escalations to the right channel.
- **Time-box the escalation.** If the human doesn't respond in N hours,
  abort the loop. Don't let loops wait forever.
- **Record the resolution.** `approval.json` (or equivalent) should
  record: who reviewed, what they decided, and any comments. This is the
  audit trail.
- **Don't escalate too eagerly.** If the loop escalates on every run,
  humans stop paying attention. Tune the threshold so escalations are
  rare and meaningful.
- **Pair with [Human Approval](human-approval.md).** Escalation is
  reactive (something went wrong); approval is proactive (something is
  about to happen). Use both for irreversible actions.
