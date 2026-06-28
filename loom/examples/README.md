# Examples

These are minimal, copy-pasteable Loopfiles for common use cases. The full canonical loops live in `loops/`.

## Minimal hello loop

```yaml
LOOM: "1.0"
name: hello-loop
version: 1.0.0
description: Hello world

OBJECTIVE: "Say hello in three languages."

AGENTS:
  - { name: builder, role: builder,  model_tier: haiku }
  - { name: judge,   role: verifier, model_tier: sonnet }

STEPS:
  - { id: s1, name: greet,  action: write_greetings, uses: builder, produces: [greetings.json] }
  - { id: s2, name: verify, action: judge_greetings, uses: judge,   depends_on: [s1] }

VERIFY:
  syntactic: ["greetings.json:valid_json"]
  semantic:  ["judge:correctness>=90"]
  confidence_threshold: 85

BUDGET: { dollars: 1, minutes: 5 }
STOP_WHEN: ["all_verify_passed"]
```

## Composing from an existing loop

```yaml
LOOM: "1.0"
name: my-coding-loop
version: 1.0.0
FROM: loom/coding-loop@1.0

# Override only what you want to change
BUDGET: { dollars: 10, minutes: 30 }
VERIFY:
  syntactic: ["tests:pass", "lint:clean"]
  semantic:  ["rubric:feature_completeness>=90"]
```

## Parallel branches

```yaml
LOOM: "1.0"
name: parallel-research
version: 1.0.0
OBJECTIVE: "Research 3 competitors in parallel."

AGENTS:
  - { name: researcher, role: researcher, model_tier: sonnet, tools: [web_search] }
  - { name: synthesizer, role: manager, model_tier: opus }

STEPS:
  - { id: s1, name: comp_a, action: research, uses: researcher, produces: [a.md], parallel: true }
  - { id: s2, name: comp_b, action: research, uses: researcher, produces: [b.md], parallel: true }
  - { id: s3, name: comp_c, action: research, uses: researcher, produces: [c.md], parallel: true }
  - { id: s4, name: synth,  action: synthesize, uses: synthesizer, depends_on: [s1, s2, s3], produces: [report.md] }

VERIFY:
  syntactic: ["report.md:valid_markdown"]
  semantic:  ["all_three_covered"]
  confidence_threshold: 85

BUDGET: { dollars: 5, minutes: 20 }
STOP_WHEN: ["all_verify_passed"]
```

## Hierarchical (manager + workers)

```yaml
LOOM: "1.0"
name: hierarchical-build
version: 1.0.0
OBJECTIVE: "Build a feature with manager + workers + verifier."

AGENTS:
  - { name: manager, role: manager,  model_tier: opus }
  - { name: coder,   role: builder,  model_tier: sonnet }
  - { name: tester,  role: builder,  model_tier: sonnet }
  - { name: judge,   role: verifier, model_tier: opus }

STEPS:
  - { id: s1, name: plan,  action: decompose,    uses: manager, produces: [plan.md] }
  - { id: s2, name: code,  action: implement,    uses: coder,   depends_on: [s1] }
  - { id: s3, name: test,  action: write_tests,  uses: tester,  depends_on: [s1], parallel: true }
  - { id: s4, name: verify, action: judge,       uses: judge,   depends_on: [s2, s3] }

VERIFY:
  syntactic: ["tests:pass", "lint:clean"]
  semantic:  ["rubric>=85"]
  external:  ["build:success"]
  confidence_threshold: 90

BUDGET: { dollars: 8, minutes: 25 }
STOP_WHEN: ["all_verify_passed"]
```
