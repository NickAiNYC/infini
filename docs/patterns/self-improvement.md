# Self Improvement Pattern

## Problem

A loop runs repeatedly. Each run, it learns something. At some point, the
lessons suggest the Loopfile itself should change — a step should be
reordered, a verifier tightened, a budget raised. You want the loop to
propose these changes to its own Loopfile.

This is the most powerful and most dangerous pattern. Use with caution.

## Diagram

```text
run → learn → [SHOULD LOOPFILE CHANGE?] → propose_change → [HUMAN APPROVAL] → apply_change
                                          └─→ continue
```

## Loopfile

Self-improvement is not a step in the loop's Loopfile — that would be
circular. Instead, it's a separate "meta-loop" that runs periodically
over the loop's lessons file.

```yaml
# meta-loop.yaml — a separate Loopfile that improves coding-loop.yaml
LOOPFILE: "1.0"
name: coding-loop-meta
version: 1.0.0

OBJECTIVE: >
  Review the last 10 runs of coding-loop. If a pattern suggests a
  Loopfile change, propose it. A human must approve before the change
  is applied.

AGENTS:
  - { name: analyst, role: researcher, model_tier: opus, tools: [read, memory] }
  - { name: editor,  role: builder,    model_tier: sonnet, tools: [read, write] }
  - { name: auditor, role: verifier,  model_tier: opus, tools: [read, audit] }

STEPS:
  - { id: s1, name: read_lessons, action: memory.read_lessons, uses: analyst, produces: [lessons.json] }
  - { id: s2, name: analyze,      action: meta.analyze_patterns, uses: analyst, depends_on: [s1], produces: [patterns.md] }
  - { id: s3, name: propose,      action: meta.propose_change,   uses: editor, depends_on: [s2], produces: [proposed-change.diff] }
  - { id: s4, name: human_approval, action: governance.await_approval, uses: auditor, depends_on: [s3], produces: [approval.json] }
  - { id: s5, name: apply,        action: meta.apply_change,     uses: editor, depends_on: [s4], produces: [Loopfile.v2.yaml] }

VERIFY:
  syntactic:
    - "proposed-change.diff:exists"
    - "approval.json:approved"
    - "Loopfile.v2.yaml:valid_loopfile"
  semantic:
    - "judge:change_improves_quality>=85"
  confidence_threshold: 90   # high bar for self-modification

STOP_WHEN: [all_verify_passed, iterations>=1]
```

## Tradeoffs

**Gives:**
- Loops that get better at being loops, not just better at their task.
- A systematic way to apply what you've learned from running a loop.

**Costs:**
- Risk of catastrophic self-modification. A meta-loop that weakens
  verification "to ship faster" is a real failure mode.
- Complexity. You now have two loops to maintain.
- Human overhead. Every proposed change needs review.

## Best practices

- **Human approval is non-negotiable.** A self-improving loop without
  human approval is a runaway. The [Human Approval](human-approval.md)
  pattern is part of this pattern.
- **High confidence threshold for changes.** A normal loop might ship at
  85% confidence; a self-modification should require 90%+. The bar is
  higher because the consequences are higher.
- **Version the Loopfile.** Every applied change creates a new version.
  Never overwrite the existing Loopfile. If the change is bad, you
  revert to the previous version.
- **Diff, don't rewrite.** The meta-loop proposes a *diff*, not a new
  Loopfile. This makes the change reviewable.
- **Audit every change.** The audit log records: what changed, who
  approved, when, and why. This is the evidence trail for
  self-modification.
- **Cap change frequency.** A meta-loop that runs every 5 minutes will
  churn the Loopfile. Run it weekly at most.
- **Don't automate away the discipline.** The Loop Engineer's job is to
  decide which proposed changes to accept. If you accept everything,
  you've delegated your discipline to a model. That's how loops degrade.
