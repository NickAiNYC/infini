# Usage

## Quickstart

```bash
pip install loom-cli
```

### Write your first Loopfile

```yaml
# ./Loopfile
LOOM: "1.0"
name: hello-loop
version: 1.0.0
description: Hello world loop

OBJECTIVE: "Say hello in three languages and verify each is correct."

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

### Validate

```bash
loom validate ./Loopfile
```

### Run

```bash
loom run ./Loopfile
```

Output:
```
▶ reading state... none found, starting fresh
▶ validated. 2 step(s) ready.
▶ trace written to runs/run_20260628T123456Z/trace.jsonl
⚠️  no engine adapter attached — install one to execute (loom engines)
```

### Inspect

```bash
loom inspect runs/run_20260628T123456Z/
```

### Replay (time-travel)

```bash
loom replay runs/run_20260628T123456Z/
# commands: n(ext), p(rev), <N>, s(tate), q(uit)
```

### Diff two versions

```bash
loom diff loops/coding-loop.yaml loops/coding-loop-v2.yaml
# 🔴 [high] VERIFY: ...
# 🟡 [medium] STEPS: ...
# 🟢 [low] version: 1.0.0 → 1.1.0
```

### Run in CI

See `.github/workflows/loop-ci.yml`. On every PR:
- All Loopfiles are validated
- `loom ci` runs against fixtures
- `loom diff` posts a semantic changelog comment

## Installing a loop from the registry

```bash
loom install loom/coding-loop@1.2
```

(Registry is in RFC. For now, copy from `loops/`.)

## Publishing your loop

```bash
loom publish ./Loopfile
```

(Registry is in RFC. For now, open a PR to `loops/`.)

## Listing compatible engines

```bash
loom engines
```

```
engine          version    spec       features
------------------------------------------------------------
langgraph       0.2.0      1.0        parallel,dag,semantic_verify
crewai          0.5.0      1.0        parallel,registry_publish
openclaw        1.0.0      1.0        parallel,dag,external
hermesagents    0.3.0      1.0        dag,semantic_verify
autogen         0.4.0      1.0        parallel,dag
smolagents      1.0.0      1.0        registry_publish
```

## Writing an engine adapter

If you maintain an agent runtime, you can make it Loom-compatible by writing an adapter that:

1. Reads a Loopfile (YAML)
2. Validates it (call `loom validate`)
3. Maps `AGENTS` to your runtime's primitives
4. Maps `STEPS` to your runtime's graph/dag/chain
5. Emits `trace.jsonl` per `spec/trace-format-v1.md`
6. Writes `loop_state.json` per `spec/state-format-v1.md`

Ship it as `loom-{your-engine}-adapter`. We will list it in `cli/adapters/README.md`.

## Using the Loop Engineer prompt

Paste `prompts/loop-engineer.md` into Claude, GPT, Cursor, or any agent runtime. The agent will operate as a Loop Engineer — refusing to ship unverified loops, escalating precisely, improving itself after every run.
