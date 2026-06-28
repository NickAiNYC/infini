# Loopfile Spec v1

> One file. Any engine. Every loop.

The **Loopfile** is a runtime-agnostic declaration of an agentic loop. It is to agent loops what a Dockerfile is to containers — a portable unit of work that any compliant engine can run, inspect, replay, and verify.

Status: **Draft v1.0** — open for community feedback.

---

## Why a Loopfile?

Today, every agent framework (LangGraph, CrewAI, AutoGen, OpenClaw, HermesAgents) reinvents the same primitives: state, resume, verification, cost ceilings, self-improvement. A loop written for one runtime is useless in another.

The Loopfile breaks that lock-in. You declare *what* the loop should do; the engine decides *how*. Loops become packages. Packages compose. The ecosystem grows without rewrites.

---

## File Format

- Filename: `Loopfile` (no extension) or `loop.yaml`
- Format: YAML 1.2
- Encoding: UTF-8
- Max size: 64 KB (loops larger than this should `include:` sub-files)

---

## Top-Level Fields

```yaml
LOOM: "1.0"                    # spec version, required
name: <string>                 # unique loop name, lowercase-kebab
version: <semver>              # loop version, required
description: <string>          # one-line summary
author: <string>               # author or org
license: <spdx>                # SPDX identifier (MIT, Apache-2.0, ...)

FROM: <loop-ref>               # optional: extend an existing loop
                              # format: registry/name@version

OBJECTIVE: <string>            # the high-level goal
SCENE: <path>                  # optional: scene_map.yaml path

INPUTS:                        # typed inputs the loop expects
  - name: <string>
    type: <string|number|boolean|file|url|json>
    required: <bool>
    default: <any>

CONSTRAINTS:                   # hard rules the loop must respect
  - <string>

AGENTS:                        # roles (engine decides implementation)
  - name: <string>
    role: <manager|builder|verifier|researcher|refiner|cost_controller|human_gate>
    model_tier: <haiku|sonnet|opus|default>
    tools: [<string>]

STEPS:                         # ordered list or DAG (via depends_on)
  - id: <string>
    name: <string>
    action: <string>
    uses: <agent_name>
    depends_on: [<step_id>]
    parallel: <bool>
    produces: [<artifact_path>]
    retry:
      max: <int>
      backoff: <exponential|linear|fixed>

VERIFY:                        # verification tiers (>=2 required for v1)
  syntactic:
    - <check>                  # e.g. "lint", "typecheck", "tests:pass"
  semantic:
    - <check>                  # e.g. "rubric:90", "judge:alignment"
  external:
    - <check>                  # e.g. "screenshot_diff:<5%", "api:200"
  confidence_threshold: <0-100>

BUDGET:                        # hard ceilings; loop halts if exceeded
  dollars: <number>
  tokens: <int>
  minutes: <int>
  external_calls: <int>

ESCALATE_WHEN:                 # human-in-the-loop triggers
  ambiguity_above: <0-1>
  confidence_below: <0-1>
  consecutive_failures: <int>
  budget_used_percent: <int>
  irreversible_action: <bool>

STOP_WHEN:                     # success conditions
  - <condition>

SELF_IMPROVE:                  # post-run hooks
  on_success:
    - <artifact_to_update>
  on_failure:
    - <artifact_to_update>
  lessons_file: <path>         # default: state/lessons.md

STATE:                         # state contract
  file: <path>                 # default: state/loop_state.json
  format: json
  resume_strategy: <continue|restart|ask>
```

---

## Minimal Example

```yaml
LOOM: "1.0"
name: dark-mode-toggle
version: 1.0.0
description: Add a dark mode toggle without breaking tests.

OBJECTIVE: "Add a dark mode toggle to the app, preserve all existing tests."

INPUTS:
  - name: repo_path
    type: file
    required: true

CONSTRAINTS:
  - no new dependencies
  - lint clean
  - no UI regressions

AGENTS:
  - { name: coder, role: builder, model_tier: sonnet, tools: [file_io, bash] }
  - { name: judge, role: verifier, model_tier: opus, tools: [bash] }

STEPS:
  - id: s1, name: plan,   action: write_plan, uses: coder, produces: [plan.md]
  - id: s2, name: code,   action: implement,  uses: coder, depends_on: [s1], produces: [src/]
  - id: s3, name: test,   action: run_tests,  uses: coder, depends_on: [s2]
  - id: s4, name: verify, action: judge,      uses: judge, depends_on: [s3]

VERIFY:
  syntactic: ["lint", "typecheck", "tests:pass"]
  semantic:  ["rubric:90"]
  external:  ["screenshot_diff:<5%"]
  confidence_threshold: 85

BUDGET: { dollars: 5, tokens: 500000, minutes: 15, external_calls: 20 }

ESCALATE_WHEN:
  ambiguity_above: 0.7
  consecutive_failures: 3
  budget_used_percent: 80
  irreversible_action: true

STOP_WHEN:
  - "all_verify_passed"
  - "confidence>=85"

SELF_IMPROVE:
  on_success: [lessons.md]
  on_failure: [lessons.md, rubric.md]
  lessons_file: state/lessons.md

STATE:
  file: state/loop_state.json
  resume_strategy: continue
```

---

## Field Reference

### `LOOM`
Spec version. Must be `"1.0"` for v1 compliance. Engines refuse incompatible versions.

### `FROM`
Optional parent loop. Inherits all fields; current file overrides. Enables composition:
```yaml
FROM: loom/coding-loop@1.2
BUDGET: { dollars: 10 }   # override only budget
```

### `INPUTS`
Typed, named inputs. Engines validate before execution. Missing required inputs escalate rather than guess.

### `STEPS`
Ordered list or DAG (via `depends_on`). `parallel: true` on independent steps lets the engine batch them.

### `VERIFY`
Three tiers. **v1 requires at least two.** Loops with only syntactic verification are marked `UNVERIFIED` in the registry.

### `BUDGET`
Hard ceiling. When any field is exceeded, the loop halts and writes a `cost_report.md`. No silent overspend.

### `ESCALATE_WHEN`
Conditions that pause execution and surface a human-readable escalation message. The loop does not continue until the human resolves or approves.

### `STOP_WHEN`
Success conditions. All must be true for the loop to declare `done`. If budget exhausts before `STOP_WHEN` is met, the loop exits with `incomplete`.

### `SELF_IMPROVE`
Post-run hooks. The minimum contract is appending to `lessons.md` after every run, success or failure.

---

## Engine Compatibility

An engine declares which spec versions and which optional features it supports:

```yaml
# engine manifest
engine: langgraph
version: 0.2.0
supports:
  loom_spec: ["1.0"]
  features: [parallel, dag, semantic_verify, registry_publish]
```

Users can check compatibility with `loom engines` and filter the registry by engine.

---

## Validation

```bash
loom validate ./Loopfile
```

Checks:
- YAML parses
- All required fields present
- `VERIFY` has at least 2 tiers
- `BUDGET` has at least one ceiling
- `STOP_WHEN` is non-empty
- `STEPS` references valid agents
- `depends_on` graph has no cycles

Invalid Loopfiles cannot be published to the registry.

---

## Versioning

- Spec version: `LOOM: "1.0"` — moves to `2.0` only on breaking changes
- Loop version: `version: <semver>` — author-controlled
- Registry pins both; `loom install loom/coding-loop@1.2` resolves the latest patch of 1.2

---

## Open Questions (for v1.1)

- Should `INPUTS` support schemas (JSON Schema) for complex types?
- Should `VERIFY` support custom judge prompts inline, or always reference a file?
- Should `STATE` support multiple backends (file, sqlite, redis)?
- Should `SELF_IMPROVE` support triggered sub-loops?

These are explicitly deferred. Ship v1, learn, iterate.

---

## License

This spec is released under CC-BY-4.0. Implementations may use any license.
