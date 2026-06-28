# Memory

Chapter 5 of the [INFINI Handbook](README.md).

> Loops that don't remember are loops that don't improve.

---

## Why memory

The single biggest difference between a senior engineer and a junior
engineer is memory. The senior engineer has seen this bug before. The
same is true for loops.

A loop without memory restarts from scratch every time. It makes the same
mistakes, hits the same dead ends, and converges on the same answer
slowly. A loop with memory carries lessons forward: it converges faster,
avoids known dead ends, and improves with each run.

Memory is what turns a loop from a one-shot into a system.

---

## The LESSONS block

The v1.0 way to add memory to a loop:

```yaml
LESSONS: { path: memory/coding-loop.md, append: true }
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

That's it. v1.0 memory is a flat markdown file, appended to after every
run, read before every run. Simple, portable, engine-agnostic.

---

## What makes a good lesson

A good lesson is:

- **Specific.** "Tests failed because of a missing import" is a lesson.
  "Be careful" is not.
- **Actionable.** The next run should be able to act on it. "Start from
  `src/App.tsx` because that's where the toggle lives" is actionable.
- **Short.** One sentence, plus metadata. Lessons accumulate; if each
  one is a paragraph, the file becomes unmanageable.
- **Honest.** Including failures. A lessons file with only successes is
  a lessons file that doesn't teach.

The Loop Engineer prompt (Rule 6) requires appending a lesson after
every run, whether the run succeeded or failed. Failed runs produce the
most valuable lessons.

---

## The MEMORY block (v1.1, planned)

v1.0's `LESSONS` block is a flat markdown file. v1.1 introduces a
structured `MEMORY` block:

```yaml
MEMORY:
  path: memory/coding-loop/
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

See [RFC-0004](../../spec/rfcs/RFC-0004-memory.md) for the full design.

---

## Cross-loop memory

A loop can reference another loop's memory:

```yaml
MEMORY:
  references:
    - memory/coding-loop/
    - memory/debug-loop/
```

This lets a `coding-loop` learn from a `debug-loop`'s prior incident
investigations. The `coding-loop` doesn't read every lesson from
`debug-loop`; it queries them semantically and gets the relevant ones.

This is how a team's loops become a system, not a collection of
individual loops.

---

## Memory and replay

Memory is part of state. When you replay a run, you replay with the
memory that existed at the time of the original run, not the current
memory. This keeps replay faithful.

You can override this with `--use-current-memory` to test "what would
this run look like with what we know now?" This is useful for evaluating
whether your lessons are actually helping.

---

## Memory failure modes

### 1. The stale lesson

A lesson from six months ago no longer applies. The codebase has
changed; the model has changed; the team has changed. The loop follows
the stale lesson and makes a wrong decision.

Defense: `decay: linear` or `decay: exponential`. Old lessons lose
weight. The loop doesn't forget them, but it stops trusting them.

### 2. The contradictory lessons

Lesson from last week: "Start from `src/App.tsx`." Lesson from this
morning: "The toggle moved to `src/components/ThemeToggle.tsx`." The loop
doesn't know which to trust.

Defense: lessons are append-only. The newer lesson wins. If you need to
*retract* a lesson, append a correction: "Ignore the lesson from
2026-06-20; the toggle has moved."

### 3. The over-fit lesson

A lesson that's too specific to one run. "Use `pytest -q -k test_auth`"
was right for that one run, but it's wrong as a general rule. The loop
follows it blindly and misses other tests.

Defense: write lessons as patterns, not commands. "When authentication
tests fail, run them in isolation first" is a pattern. "Run
`pytest -q -k test_auth`" is a command.

### 4. The bloated memory

A lessons file with 1000 entries. The planner's context fills with
lessons; the actual plan gets lost.

Defense: `max_entries: 100`. The engine keeps the most recent 100 (or,
in v1.1, the 100 most relevant). Old lessons are archived, not deleted.

---

## What's next

- Chapter 6, [Observability](observability.md) — loops you can see.
- For the normative spec, see [RFC-0004](../../spec/rfcs/RFC-0004-memory.md).
- For memory patterns, see [`docs/patterns/memory-update.md`](../patterns/memory-update.md).
