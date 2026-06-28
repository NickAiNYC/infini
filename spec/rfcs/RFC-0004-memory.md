# RFC-0004: Loop Memory

- Start date: 2026-06-28
- Status: draft
- Spec version: 1.0 (LESSONS), 1.1 (full memory)
- PR: TBD
- Implementation: `LESSONS` ships in 1.0; full memory model in 1.1

## Summary

Defines how loops remember across runs. Memory is what turns a loop from a
one-shot into a system that improves. A loop without memory restarts from
scratch every time; a loop with memory carries lessons forward.

## Motivation

The single biggest difference between a senior engineer and a junior
engineer is memory. The senior engineer has seen this bug before. The same
is true for loops.

Memory must be:

- **Declared.** A loop opts into memory; it doesn't get it by default.
  Memory has cost (storage, retrieval latency) and risk (stale lessons
  leading the loop astray).
- **Append-only by default.** Lessons are added, never edited. Editing is
  a human action.
- **Retrievable.** A loop can query its own memory during planning.
- **Portable.** Memory is part of the loop's state, not the engine's.
  Swapping engines does not lose memory.

## Detailed design

### LESSONS block (v1.0)

```yaml
LESSONS: { path: memory/<loop-name>.md, append: true }
```

After every run, the engine appends a lesson to the file. A lesson is a
single sentence plus metadata:

```markdown
## 2026-06-28 10:47 — run 2026-06-28-1042 — verified

The dark-mode toggle was implemented in 4 minutes because the prior run
had already identified the right file. Continue starting from `src/App.tsx`.

- iterations: 2
- cost: $1.70
- confidence: 91
- artifacts: 9
```

Before every run, the engine reads the lessons file and includes the most
recent N entries in the planner's context.

### MEMORY block (v1.1, planned)

The v1.0 `LESSONS` block is a flat markdown file. v1.1 introduces a
structured `MEMORY` block:

```yaml
MEMORY:
  path: memory/<loop-name>/
  retrieval: semantic      # semantic | recent | manual
  max_entries: 100
  decay: linear            # linear | exponential | none
  decay_rate: 0.95
```

This enables:

- **Semantic retrieval.** The loop queries memory by meaning, not by
  recency. "Show me lessons about authentication failures."
- **Decay.** Old lessons lose weight. The loop doesn't forget them, but
  trusts recent lessons more.
- **Structured entries.** Each memory entry is a JSON object with tags,
  outcomes, and references to the run that produced it.

### Memory across loops

A loop can reference another loop's memory:

```yaml
MEMORY:
  references:
    - memory/coding-loop/
    - memory/debug-loop/
```

This lets a `coding-loop` learn from a `debug-loop`'s prior incident
investigations.

### Memory and replay

Memory is part of state. When you replay a run, you replay with the memory
that existed at the time of the original run, not the current memory. This
keeps replay faithful.

You can override this with `--use-current-memory` to test "what would this
run look like with what we know now?"

## Alternatives considered

- **No memory (loops are stateless).** Rejected — this is the status quo
  for chains. The whole point of a loop is that it improves.
- **Engine-managed memory.** Rejected — memory would not survive engine
  swaps. Memory is part of the loop.
- **Free-form memory (no structure).** Rejected — `LESSONS` is free-form
  in v1.0 as a starting point, but structured memory in v1.1 enables
  retrieval and decay.
- **Memory edits allowed by the loop.** Rejected — lessons are
  append-only. If a lesson is wrong, the next run adds a correction.
  Editing memory is a human action.

## Backwards compatibility

v1.0. `LESSONS` is part of v1.0. `MEMORY` is additive in v1.1.

## Conformance impact

Memory is not a conformance capability. Engines may implement it or not.
Engines that don't implement `LESSONS` ignore the block but still execute
the loop. This is tracked in the compatibility matrix as a `Memory` column
(planned for v1.1).

## Open questions

- Should memory be shared across namespaces, or always scoped to the loop?
  Current answer: scoped to the loop, with explicit `references:` to opt
  into cross-loop memory.
- How is memory garbage-collected? Current answer: `decay`, plus a
  human-triggered prune. Open for debate.
- Should memory be signed? Current answer: no, it's local state. If a loop
  is published with memory, the memory is stripped.

## Future possibilities

- v1.1: structured `MEMORY` block with semantic retrieval.
- v1.2: memory packs — pre-baked memory for a category (e.g., "SRE
  incident memory pack").
- v2.0: memory marketplace — share and subscribe to memory from other
  teams.

## Acknowledgements

The memory model is borrowed from the SRE Book (postmortems as
organizational memory), LangGraph's checkpointing, and Claude's
artifact-based memory.
