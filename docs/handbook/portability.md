# Portability

Chapter 9 of the [INFINI Handbook](README.md).

> A loop that only runs on one engine is a chain with extra steps.

---

## Why portability

Engines multiply. LangGraph today, something else tomorrow. Models get
cheaper. New frameworks appear. Teams switch stacks.

If your loops are pinned to one runtime, every engine swap is a rewrite.
You lose the loops, the traces, the lessons, the muscle memory.

If your loops are portable, an engine swap is a config change. The
Loopfile doesn't change; the `ENGINE` block does. The traces still work
(they're engine-agnostic). The lessons still apply (they're stored as
markdown). The muscle memory still applies (the discipline is the same).

Portability is the bet that pays for everything else.

---

## What makes a Loopfile portable

A portable Loopfile:

1. **Declares `model_tier`, not model names.** `model_tier: sonnet` is
   portable; `model: claude-3-5-sonnet-20241022` is not.
2. **Declares `action` names, not tool implementations.** `action:
   file_system.write` is portable; `action: subprocess.run(["vim", ...])`
   is not.
3. **Declares `role`, not agent classes.** `role: builder` is portable;
   `agent: langgraph.CodeAgent` is not.
4. **Uses only spec-defined fields.** Engine-specific extensions (Hermes
   governance, OpenClaw tools) go in the `ENGINE` block, not in `STEPS`.
5. **Declares verification in spec terms.** `judge:correctness>=90` is
   portable; a custom Python verifier is not.

If you follow these five rules, your Loopfile runs on any conforming
engine. The reference engine, Hermes, OpenClaw, and (eventually)
LangGraph, CrewAI, AutoGen, and the rest.

---

## The ENGINE block

The `ENGINE` block is the only part of a Loopfile that's
engine-specific. It's also the only part that's optional — a Loopfile
without an `ENGINE` block runs on the reference engine.

```yaml
ENGINE:
  type: hermes                  # or openclaw, langgraph, etc.
  adapter: adapters/hermes
  governance:
    memory: true
    audit_log: true
    budget_policy: strict
    escalation_policy: enabled
  delegates:                    # for hybrid mode
    execution:
      type: openclaw
      adapter: adapters/openclaw
      tools: [file_system, terminal, github]
```

To swap engines, change the `ENGINE` block. Nothing else.

This is the Docker move. A Dockerfile runs on any container runtime
because the runtime-specific bits are in the runtime, not the Dockerfile.
A Loopfile runs on any engine because the engine-specific bits are in the
`ENGINE` block, not in the rest of the Loopfile.

---

## The compatibility matrix

Not every engine supports every feature. The compatibility matrix in
[`spec/compatibility.md`](../../spec/compatibility.md) tracks which
engines implement which capabilities.

| Engine | Parse | Run | Verify | Inspect | Replay | Diff |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| INFINI Reference | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hermes | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 |
| OpenClaw | ✅ | ✅ | ✅ | ✅ | 🚧 | 🚧 |
| LangGraph | ✅ | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 |

A Loopfile that uses only `Parse`, `Run`, `Verify`, and `Inspect` is
portable across all four engines today. A Loopfile that uses `Replay` is
portable across INFINI Reference and Hermes today, and across OpenClaw
when its replay support ships.

Write to the matrix, not to the engine. If you need a feature only one
engine supports, you've lost portability. Either drop the feature or wait
for the other engines to catch up.

---

## The portability tax

Portability isn't free. The tax is:

1. **You can't use engine-specific features.** If LangGraph has a cool
   new feature, you can't use it in a portable Loopfile until it's in
   the spec.
2. **You declare intent, not implementation.** `action: file_system.write`
   is intent; `subprocess.run(...)` is implementation. Intent is weaker
   — the engine decides how to fulfill it. This is usually fine; sometimes
   it's limiting.
3. **You test on multiple engines.** A Loopfile that works on the
   reference engine might fail on Hermes because of a conformance gap.
   CI should run on at least two engines.

The tax is worth paying. The alternative — rewriting loops every time you
swap engines — is more expensive.

---

## The portability ladder

Not every Loopfile needs to be fully portable. There's a ladder:

1. **Reference-only.** Runs on the INFINI Reference Engine. Useful for
   development and testing. Not production-portable.
2. **Single-engine.** Runs on one adapter (Hermes, OpenClaw, etc.). Useful
   when you've committed to one runtime. Portable to other engines only
   if they implement the same capabilities.
3. **Multi-engine.** Runs on two or more adapters. The hybrid demo is
   this — Hermes and OpenClaw. This is where portability starts to pay.
4. **Fully portable.** Runs on every conforming engine. Uses only
   spec-defined features. This is the goal for canonical loops.

The 12 canonical loops aim for rung 4. Your loops can be on any rung;
just know which rung you're on.

---

## What's next

- Chapter 10, [Standards](standards.md) — why this is a standard, not a tool.
- For the compatibility matrix, see [`spec/compatibility.md`](../../spec/compatibility.md).
- For the adapter interface, see [`sdk/`](../../sdk/).
