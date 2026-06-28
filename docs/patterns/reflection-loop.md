# Reflection Loop Pattern

## Problem

A step produces output. Before shipping, you want a second agent to
critique the output — not just verify it, but explain what's wrong with
it. The critique feeds back into a revision step.

This is the loop in "loop." Without reflection, you have a chain that
happens to repeat; with reflection, you have a system that improves.

## Diagram

```text
produce → critique → [improve?] → produce' → critique' → [ship]
```

## Loopfile

```yaml
STEPS:
  - { id: s1, name: draft,    action: content.draft,   uses: drafter, produces: [draft.md] }
  - { id: s2, name: critique, action: content.critique, uses: critic,  depends_on: [s1], produces: [critique.md] }
  - { id: s3, name: revise,   action: content.revise,   uses: drafter, depends_on: [s1, s2], produces: [revised.md] }
  - { id: s4, name: polish,   action: content.polish,   uses: editor,  depends_on: [s3], produces: [final.md] }

VERIFY:
  syntactic: ["final.md:exists"]
  semantic:
    - "judge:quality>=85"
    - "judge:critique_addressed>=80"   # the revise step addressed the critique
  confidence_threshold: 85
```

## Tradeoffs

**Gives:**
- Output that's been reviewed before shipping.
- A natural place to encode quality criteria.

**Costs:**
- Two model calls per iteration (produce + critique). Doubles the cost.
- If the critic is too lenient, the reflection is theater. If too harsh,
  the loop never converges.

## Best practices

- **Use a different model tier for the critic.** If the drafter is
  `sonnet`, the critic should be `opus` (or vice versa). Same-model
  critics tend to sycophancy.
- **Make the critique specific.** "This is bad" is not a critique.
  "Paragraph 3 makes an unsupported claim; cite a source or remove it"
  is.
- **Verify that the critique was addressed.** The
  `judge:critique_addressed>=80` check is essential. Without it, the
  drafter can ignore the critique and the loop ships anyway.
- **Cap iterations.** A reflection loop that never converges will spend
  your entire budget. `STOP_WHEN: [all_verify_passed, iterations>=3]`.
- **Pair with [Memory Update](memory-update.md).** After the loop ships,
  append a lesson: "The critique caught X; in future runs, check for X
  in the draft step."
