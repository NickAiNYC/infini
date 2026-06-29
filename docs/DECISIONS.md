# Design Decisions

Lightweight records of significant spec changes.
For detailed architecture decisions, see [`adr/`](adr/).

## 2026-06-29 — Curated examples to 4 intentional demos

**What:** Moved 8 older examples to `_deprecated/`, renamed 2 directories,
rewrote `examples/README.md` as a curated table.

**Reason:** The examples directory had grown organically into a collection
of demos without clear progression. New users had no way to know where
to start. The curated set (hello-world → claim-audit → github-pr-review
→ squad-loop) forms a natural learning path from smallest valid Loopfile
through multi-agent orchestration.

**Alternatives considered:**
- Keep everything and add a "start here" tag — didn't solve the clutter
- Delete deprecated examples outright — lost historical context

**Trade-offs:**
- Loses discoverability of old examples for existing users
- `_deprecated/` preserves content without polluting the curated view
- Renamed directories (hermes-governed-growth → claim-audit, openclaw-agent-loop → github-pr-review) break existing bookmarks

---

## 2026-06-29 — Added `prompt` field to AGENTS

**What:** Added `prompt` (optional string) to the agent schema. When
present, the engine uses it as the agent's directive, run against
accumulated context.

**Reason:** The original `role` field was too coarse to express what
an agent should actually do. A `role: researcher` doesn't tell the
engine what research to perform or how to format output. `prompt`
bridges declarative intent and executable instruction without pinning
the agent to a specific model.

**Alternatives considered:**
- Keep `role` as the only directive and let engines infer behaviour
  (too vague — each engine would interpret differently)
- Use `instruction` instead of `prompt` (`prompt` is more standard
  in the LLM ecosystem)

**Trade-offs:**
- Adds a heavy string field to an otherwise lean schema
- Creates expectation that the prompt is the *only* instruction (it's
  additive — engines may prepend system prompts)
- Increases Loopfile size, especially for multi-agent loops

**Related:** [RFC-0012](https://github.com/NickAiNYC/infini/issues/new?template=rfc.md) — Prompt field semantics (proposed)

---

## 2026-06-29 — Added `command` field to STEPS

**What:** Added `command` (optional string) to the step schema. A shell
escape hatch for literal command-line logic.

**Reason:** Some steps genuinely need shell-level control — parsing
a JSON report and exiting with a code, running a linter, checking
environment state. Without `command`, every step would need an agent,
which is overkill and expensive for deterministic operations.

**Constraint:** `command` is an escape hatch, not the primary path.
If every step in a Loopfile uses `command`, the file is a shell script
in YAML clothing, not a declarative workflow. Engines SHOULD prefer
the agent+action path and reserve `command` for steps where shell
control is the clearest expression.

**Alternatives considered:**
- Require an agent for every step (costly, indirect)
- Define a `shell` action type (same thing, different shape)
- Omit entirely and let engines provide their own `command` extension
  (would fragment — every engine's escape hatch would differ)

**Trade-offs:**
- Risk of `command` becoming the default path rather than the exception
- No portability guarantee (a shell command that works on Linux may
  not work on macOS or Windows)
- Necessary for real-world utility — without it, simple operations
  require spinning up an agent

---

## 2026-06-29 — Added `artifacts` to memory config

**What:** Added `artifacts` (optional array of strings) to the
`memory` block, listing file paths to persist across loop runs.

**Reason:** Loops that produce files (test reports, generated code,
verification output) need a way to declare which artifacts should
survive between iterations. Without it, each loop run starts from
scratch with no accumulated output.

**Alternatives considered:**
- Auto-persist everything in `produces` (artifacts and intermediate
  outputs have different lifetimes)
- Use `LESSONS` block for artifacts (lessons are semantic insights,
  not file paths)

**Trade-offs:**
- Adds another field to memory config
- Path resolution depends on engine working directory
- No wildcard/glob support yet (explicit paths only)

---

## 2026-06-29 — Add squad-loop example

**What:** Created `examples/squad-loop/` — a declarative mapping of
multi-agent handoff (plan → expand → implement → verify), inspired
by [Squad CLI](https://github.com/tom-doerr/squad_cli).

**Reason:** Squad showed that developers want multi-agent collaboration
but are building ad hoc imperative tools to get it. The Loopfile
demonstrates the same pipeline declaratively: 4 agents, 5 steps,
budget enforcement, verification assertions.

**Positioning note:** This example is a *declarative mapping of a
multi-agent handoff pattern*, not a live Claude/Gemini/Codex
orchestration. It illustrates the model; actual execution depends on
the engine and available models.
