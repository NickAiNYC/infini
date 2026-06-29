# Hello World

> The simplest valid Loopfile. One agent, one step, one artifact.

## What this demonstrates

- Minimal valid Loopfile structure
- Single-agent execution pattern
- `infini run` → `infini inspect` → `infini replay` workflow

## Run it

```bash
infini validate examples/hello-world/Loopfile.yaml
infini run examples/hello-world/Loopfile.yaml --mock

# Inspect the trace
infini inspect runs/latest/

# Replay from scratch
infini replay runs/latest/
```

## The Loopfile

```yaml
LOOPFILE: "1.0"
name: hello-world
version: 1.0.0
description: "The simplest possible Loopfile. One agent, one step, one artifact."

OBJECTIVE: "Write a greeting message to greeting.txt."

AGENTS:
  - { name: greeter, role: builder, model_tier: haiku }

STEPS:
  - { id: s1, name: greet, action: write_greeting, uses: greeter, produces: [greeting.txt] }

VERIFY:
  syntactic: ["greeting.txt:exists"]
  semantic: []
  confidence_threshold: 0

BUDGET: { dollars: 1, minutes: 2 }
STOP_WHEN: ["all_verify_passed"]
```

Start here before moving to the more complex examples.
