# Examples

The 12 canonical loops live in `loops/`. Each is a working Loopfile with documentation in its YAML comments.

## By use case

### Coding
- [`coding-loop`](../loops/coding-loop.yaml) — implement a feature, preserve tests
- [`refactor-loop`](../loops/refactor-loop.yaml) — refactor without behavior change
- [`test-gen-loop`](../loops/test-gen-loop.yaml) — generate tests to coverage target
- [`debug-loop`](../loops/debug-loop.yaml) — reproduce, isolate, fix, verify

### Review
- [`review-loop`](../loops/review-loop.yaml) — code review with rubric + cross-check

### Research & content
- [`research-loop`](../loops/research-loop.yaml) — multi-source research with citations
- [`content-loop`](../loops/content-loop.yaml) — draft → critique → revise

### Operations
- [`migration-loop`](../loops/migration-loop.yaml) — migrate across versions
- [`doc-sync-loop`](../loops/doc-sync-loop.yaml) — keep docs in sync with code
- [`oncall-loop`](../loops/oncall-loop.yaml) — triage incidents
- [`sre-loop`](../loops/sre-loop.yaml) — investigate, mitigate, postmortem

### Growth
- [`outreach-loop`](../loops/outreach-loop.yaml) — personalized outreach at scale

## Composing loops

Loops compose via `FROM:`

```yaml
# MyLoopfile
LOOM: "1.0"
name: my-coding-loop
version: 1.0.0
FROM: loom/coding-loop@1.0

BUDGET: { dollars: 10 }   # override only what you want to change
VERIFY:
  syntactic: ["tests:pass", "lint:clean", "typecheck:pass"]
  semantic:  ["rubric:feature_completeness>=90"]
```

Anything not overridden is inherited.

## Writing your own

1. Start from the closest canonical loop
2. Copy it to `./Loopfile`
3. Modify the `OBJECTIVE`, `INPUTS`, `VERIFY`, `STOP_WHEN`
4. Run `loom validate`
5. Run `loom run`
6. Inspect with `loom inspect`
7. Iterate

## Contributing back

If your loop is general-purpose, consider contributing it back as a canonical. See `CONTRIBUTING.md`.
