# RFC-0011: Agentic Loop Primitives for INFINI v1.1

- Start date: 2026-06-29
- Status: draft
- Spec version: 1.1 (additive)
- PR: TBD
- Implementation: TBD

## Summary

Extend INFINI's declarative Loopfile with first-class support for dynamic agentic loops, self-reflection, and swarm coordination.

## Motivation

INFINI v1.0 excels at portable workflows — declarative pipelines that run on any engine. But the industry is moving toward fully dynamic, self-improving agent systems. Agents that revise their own output, coordinate in swarms, and generate sub-loops at runtime.

Static workflows are the "Hello World" of agents. Real agents revise, reflect, and swarm. INFINI v1.1 makes these patterns declarative.

## Proposed Syntax

### REVISE Block

Self-revision: when a step fails or has low confidence, automatically re-execute with a revised strategy.

```yaml
REVISE:
  condition: "step.failed or step.confidence < 0.5"
  target: research
  strategy: "replan"        # replan | refine | fallback
  max_attempts: 3
  on_success: continue       # continue | stop | escalate
  on_failure: escalate       # continue | stop | escalate
```

- `condition`: evaluated after the target step completes. If true, revision triggers.
- `strategy`: how the agent should approach the retry.
  - `replan`: generate a new plan before re-executing
  - `refine`: adjust the prompt/context and re-execute
  - `fallback`: switch to a simpler/cheaper approach
- `max_attempts`: hard cap on revision iterations.
- `on_success`/`on_failure`: what to do after revision succeeds or exhausts attempts.

### SWARM Block

Multi-agent coordination: multiple agents work in parallel, share results, and converge.

```yaml
SWARM:
  agents:
    - role: "researcher"
      uses: research-agent
      model_tier: sonnet
    - role: "validator"
      uses: validator-agent
      model_tier: haiku
    - role: "critic"
      uses: critic-agent
      model_tier: sonnet
  coordinator: "consensus"   # majority | consensus | hierarchical
  max_rounds: 5
  converge_condition: "all_agents.consensus >= 0.8"
  share_results: true         # agents see each other's output between rounds
```

- `coordinator`: how to aggregate agent outputs.
  - `majority`: take the output agreed upon by >50% of agents
  - `consensus`: require all agents to agree (or reach threshold)
  - `hierarchical`: a designated lead agent makes the final call
- `max_rounds`: hard cap on coordination rounds.
- `converge_condition`: when to stop iterating.
- `share_results`: whether agents see each other's output between rounds.

### COMPOSE Block

Dynamic sub-loops: generate and execute sub-loops at runtime.

```yaml
COMPOSE:
  source: dynamic             # dynamic | static
  generator: generate_sub_loop  # step that produces sub-Loopfiles
  iterations: loop            # how many sub-loops to run (number or "loop" for until-done)
  aggregate: "concat"         # sum | concat | list | merge
  parallel: true              # run sub-loops in parallel
```

- `source`: `dynamic` (generated at runtime) or `static` (predefined list).
- `generator`: the step that produces sub-Loopfile definitions.
- `iterations`: how many sub-loops to execute.
- `aggregate`: how to combine sub-loop results.
- `parallel`: whether to run sub-loops concurrently.

## Example: Self-Revising Research Agent

```yaml
LOOPFILE: "1.1"
name: self-revising-research
version: 1.0.0

OBJECTIVE: "Research a topic with at least 5 credible sources."

AGENTS:
  - { name: researcher, role: researcher, model_tier: sonnet, tools: [browser] }
  - { name: validator, role: verifier, model_tier: haiku }
  - { name: critic, role: critic, model_tier: sonnet }

STEPS:
  - id: s1
    name: research
    action: browser.search
    uses: researcher
    produces: [sources.json]

  - id: s2
    name: validate
    action: evaluate_credibility
    uses: validator
    depends_on: [s1]
    produces: [credibility.json]

  - id: s3
    name: check_gaps
    action: check_completeness
    uses: critic
    depends_on: [s2]
    produces: [gaps.json]

REVISE:
  condition: "gaps.length > 0 or credibility.score < 0.8"
  target: s1
  strategy: refine
  max_attempts: 3
  on_success: continue
  on_failure: escalate

VERIFY:
  syntactic: ["sources.json:at_least_five_sources"]
  semantic: ["judge:credibility>=0.8"]
  confidence_threshold: 85

BUDGET: { dollars: 10, minutes: 30 }
STOP_WHEN: ["all_verify_passed", "iterations>=5"]
```

## Example: Swarm Consensus Agent

```yaml
LOOPFILE: "1.1"
name: swarm-consensus
version: 1.0.0

OBJECTIVE: "Three agents independently analyze a question and reach consensus."

SWARM:
  agents:
    - role: "analyst"
      uses: analyst-agent
      model_tier: sonnet
    - role: "skeptic"
      uses: skeptic-agent
      model_tier: sonnet
    - role: "synthesizer"
      uses: synthesizer-agent
      model_tier: opus
  coordinator: "consensus"
  max_rounds: 3
  converge_condition: "consensus_score >= 0.85"
  share_results: true

VERIFY:
  syntactic: ["consensus.json:exists"]
  semantic: ["judge:agreement>=85"]
  confidence_threshold: 85

BUDGET: { dollars: 15, minutes: 20 }
STOP_WHEN: ["all_verify_passed", "iterations>=3"]
```

## Backward Compatibility

All new blocks are **optional**. Existing v1.0 Loopfiles continue to work unchanged. The `LOOPFILE: "1.1"` version string is additive — a v1.0 engine that encounters REVISE/SWARM/COMPOSE blocks should ignore them and warn.

## Implementation Plan

| Phase | What | Timeline |
| --- | --- | --- |
| 1 | Syntax design + schema extension | Week 1 |
| 2 | REVISE in reference engine | Week 2 |
| 3 | SWARM coordinator | Week 3 |
| 4 | COMPOSE engine | Week 3 |
| 5 | Examples + documentation | Week 4 |

## Alternatives Considered

- **Imperative loops in Python**: Rejected — breaks portability. The whole point of INFINI is declarative.
- **Conditional steps via `if`**: Rejected — too low-level. REVISE is a higher-level abstraction.
- **External orchestration**: Rejected — the loop logic should live in the Loopfile, not in glue code.

## Open Questions

- Should SWARM agents be able to spawn their own SWARM blocks? (recursive swarms)
- Should COMPOSE support streaming aggregation (process results as they arrive)?
- How should REVISE interact with BUDGET? (does revision cost count toward the budget?)
