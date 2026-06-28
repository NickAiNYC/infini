<p align="center">
  <img src="assets/hero.png" alt="InFini" width="100%" />
</p>

<h1 align="center">Loom</h1>
<p align="center"><b>Loops that ship. Loops that learn.</b></p>
<p align="center">
  The open standard for agent loops. Write a <code>Loopfile</code>, run it on any engine.
</p>
<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-blue.svg" /></a>
  <img src="https://img.shields.io/badge/spec-v1.0-indigo" />
  <img src="https://img.shields.io/badge/loops-12_cyan" />
</p>

---

## The 30-second pitch

The agent ecosystem has 100 frameworks and zero standards. Loom fixes that.

```yaml
# Loopfile
LOOM: "1.0"
name: dark-mode-toggle
OBJECTIVE: "Add a dark mode toggle, preserve tests"
BUDGET: { dollars: 5, minutes: 15 }
VERIFY:
  syntactic: ["tests:pass", "lint"]
  semantic:  ["rubric:90"]
STOP_WHEN: ["all_verify_passed"]
```

```bash
$ loom run
▶ reading state... none found, starting fresh
▶ executing: plan → code → test → verify
▶ verification: tests PASS · rubric 92/100 PASS
▶ cost: $1.84 / $5.00 · 4m32s / 15m
✓ shipped. state saved. lessons appended.
```

**One file. Any engine. Every loop.**

---

## Why Loom exists

Every agent framework today — LangGraph, CrewAI, AutoGen, OpenClaw, HermesAgents — reinvents the same five primitives: state, resume, verification, cost ceilings, self-improvement. A loop written for one runtime is useless in another.

Docker didn't win because of Docker Engine. Docker won because of **Dockerfile + Registry + Hub**. The engine got commoditized; the format ate the world.

Loom is the Dockerfile for agent loops. We don't ship a runtime. We ship the format the runtimes agree on.

📖 **Read the [Manifesto](MANIFESTO.md)** — *Loops > Chains*

---

## Install

```bash
# CLI (Python 3.10+)
pip install loom-cli

# Or from source
git clone https://github.com/loom-spec/loom
cd loom && pip install -e .
```

---

## Quickstart

### 1. Write a Loopfile

```yaml
# ./Loopfile
LOOM: "1.0"
name: my-first-loop
version: 1.0.0
description: Hello world loop

OBJECTIVE: "Say hello in three languages and verify each is correct."

AGENTS:
  - { name: builder, role: builder, model_tier: haiku }
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

### 2. Run it

```bash
loom run ./Loopfile
```

### 3. Inspect the run

```bash
loom inspect runs/latest/
```

Opens an interactive trace: every step, every token, every decision, every cost.

### 4. Replay if something went wrong

```bash
loom replay runs/latest/ --step s2
```

Time-travel to any decision point. Inspect state. Change inputs. Re-run from there.

---

## The 12 canonical loops

Curated, versioned, benchmarked. Each ships with a Loopfile + essay + fixtures.

| Loop | What it does |
|------|-------------|
| [`coding-loop`](loops/coding-loop.yaml) | Implement a feature, preserve tests |
| [`refactor-loop`](loops/refactor-loop.yaml) | Refactor a module without behavior change |
| [`test-gen-loop`](loops/test-gen-loop.yaml) | Generate tests until coverage hits target |
| [`debug-loop`](loops/debug-loop.yaml) | Reproduce, isolate, fix, verify a bug |
| [`review-loop`](loops/review-loop.yaml) | Code review with rubric + cross-check |
| [`research-loop`](loops/research-loop.yaml) | Multi-source research with citations |
| [`content-loop`](loops/content-loop.yaml) | Draft → critique → revise content |
| [`outreach-loop`](loops/outreach-loop.yaml) | Personalized outreach at scale |
| [`migration-loop`](loops/migration-loop.yaml) | Migrate code across versions |
| [`doc-sync-loop`](loops/doc-sync-loop.yaml) | Keep docs in sync with code |
| [`oncall-loop`](loops/oncall-loop.yaml) | Triage incidents, propose fixes |
| [`sre-loop`](loops/sre-loop.yaml) | Investigate, mitigate, postmortem |

Browse them all in [`loops/`](loops/). Install any: `loom install loom/coding-loop@1.0`.

---

## The CLI

```bash
loom run        [Loopfile]      # execute a loop
loom validate   [Loopfile]      # check spec compliance
loom inspect    [run_dir]       # visualize a run trace
loom replay     [run_dir]       # time-travel debug
loom diff       [v1] [v2]       # semantic diff between loop versions
loom install    [loop_ref]      # pull from registry
loom publish    [Loopfile]      # push to registry
loom ci         [Loopfile]      # run loop against fixtures (GitHub Action)
loom engines                    # list compatible engines
loom search     [query]         # search the registry
```

---

## The Registry

`loom publish` pushes your Loopfile to the public registry. `loom install` pulls. Versions are immutable and signed.

```bash
loom install loom/coding-loop@1.2
loom search "research loop with citations"
loom publish ./Loopfile
```

Browse: <https://registry.loom.dev> (coming soon — see [`registry/README.md`](registry/README.md))

---

## Loom CI

Run your loops on every PR. Catch regressions before merge.

```yaml
# .github/workflows/loop-ci.yml
name: Loop CI
on: [pull_request]
jobs:
  loom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: loom/ci@v1
        with:
          loopfile: ./loops/coding-loop.yaml
          fixtures: ./tests/fixtures/
          expect:   ./tests/expected/
```

If a PR changes a Loopfile, `loom diff` runs automatically and posts a comment explaining the semantic change.

---

## The Loop Engineer Prompt

Loom ships with the canonical definition of a new role: **Loop Engineer**. Paste it into any agent runtime and it operates as a Loop Engineer — refusing to ship unverified loops, escalating precisely, improving itself after every run.

📖 **Read it: [`prompts/loop-engineer.md`](prompts/loop-engineer.md)**

This is the "Google SRE Book" move for agents: define the discipline, own the discipline.

---

## Why this is viral

- **The wedge:** first portable format for agent loops
- **The analogy:** "Dockerfile for AI agents" — 5-second comprehension
- **The enemy:** "Chains are scripts. Loops are systems."
- **The role:** defines "Loop Engineer" as a job title
- **The anthology:** 12 canonical loops = the Design Patterns book for AI workers
- **The tooling:** inspect + replay + diff = the debugger the ecosystem doesn't have

---

## Contributing

We accept:
- Loopfile spec improvements (RFCs in `spec/`)
- New canonical loops (PRs to `loops/`)
- Engine adapters (any runtime that can parse Loopfiles)
- Inspector / replay / diff improvements (`cli/`)
- Essays and benchmarks (`docs/`)

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first. Sign your commits. Be excellent to each other.

---

## Community

- **Discord:** <https://discord.gg/loom-dev> (coming soon)
- **Discussions:** GitHub Discussions
- **RFCs:** `spec/rfcs/` directory
- **Office hours:** weekly, see `docs/community.md`

---

## License

- **Spec:** CC-BY-4.0 (`spec/`)
- **Code:** MIT (`cli/`, `ci/`)
- **Loops:** MIT (`loops/`, `examples/`)
- **Docs:** CC-BY-4.0 (`docs/`, `MANIFESTO.md`)

See [`LICENSE`](LICENSE).

---

## Status

Spec v1.0 — draft, open for community feedback. The CLI ships with reference implementations of `validate`, `inspect`, `replay`, `diff`, and `ci`. The `run`, `publish`, and `install` commands require an engine adapter (LangGraph adapter ships Q1).

**We are shipping first. Join us.**

<p align="center"><b>Loops that ship. Loops that learn.</b></p>
