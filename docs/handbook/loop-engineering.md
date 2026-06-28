# Loop Engineering

Chapter 3 of the [INFINI Handbook](README.md).

---

## The role

A **Loop Engineer** is someone who:

- refuses to ship unverified loops,
- escalates precisely — not too early, not too late,
- treats every run as a learning opportunity,
- writes loops that other engines can run without modification,
- debugs loops with `infini inspect` and `infini replay`, not with `print`
  statements,
- benchmarks loops on cost, runtime, and verification rate — and publishes
  the results.

This role will exist whether INFINI names it or not. We're naming it early
so the discipline has a home.

The canonical Loop Engineer prompt is at
[`prompts/loop-engineer.md`](../../prompts/loop-engineer.md). Paste it
into any agent runtime and it operates as a Loop Engineer.

---

## The six rules

The Loop Engineer prompt encodes six rules. This chapter explains each.

### 1. Observe before you plan

Every loop starts by reading state. What already exists? What did the
last run produce? What lessons did it learn?

A loop that doesn't observe is a loop that repeats itself. The first step
of every canonical loop is a `recall` or `discover` step — not a `plan`
step.

This is the difference between a loop and a chain. A chain starts
executing; a loop starts by reading the world.

### 2. Plan before you execute

State the plan in one paragraph. Name the steps. Name the artifacts each
step will produce. Name the verification you will run.

This sounds obvious. It is not. Most agent systems skip planning and go
straight to execution. The result is agents that produce work no one can
audit. Planning is what makes the loop's behavior legible to the humans
who have to trust it.

### 3. Execute against a budget

Every loop has a dollar ceiling and a wall-clock ceiling. You must
enforce both. If you approach either, you stop and escalate — you do not
silently overrun.

A loop without a budget is a loop that can spend forever. Budgets turn
"this might work" into "this might work, and if it doesn't, it fails
cheaply."

### 4. Verify before you ship

A loop that exits without verification is not shipped, it is abandoned.
You must declare, in the Loopfile's `VERIFY` block, what counts as "done"
and how to check it. If you cannot declare verification, you do not ship.

Verification is covered in detail in [Chapter 4](verification.md). It is
the single most important rule.

### 5. Critique before you improve

When a step fails or a verifier rejects your output, you do not retry
blindly. You write down, in one sentence, why it failed. Then you change
one thing. Then you retry.

Blind retries are forbidden. They're how loops spiral. A loop that
retries without critique is a loop that doesn't learn — it just spends
money until it lucks into a pass.

### 6. Improve after every run

Whether the loop succeeded or failed, you append a lesson learned to the
loop's `LESSONS` file. Future runs of the same loop must read those
lessons before planning.

This is what makes a loop a system, not a one-shot. Memory is covered in
[Chapter 5](memory.md).

---

## How to write your first loop

1. **Write the `OBJECTIVE` first.** One sentence. If you can't write it
   in one sentence, you don't have a loop yet — you have a vibe.
2. **Write the `VERIFY` block next.** What does "done" look like? If you
   can't answer this, stop. Don't write `STEPS` until you can.
3. **Write `BUDGET`.** How much money and time is this worth? If you
   don't know, start small ($1, 5 minutes) and scale up.
4. **Write `STEPS`.** Now you can plan. Each step should produce an
   artifact; each artifact should be verifiable.
5. **Write `STOP_WHEN`.** At minimum, `all_verify_passed`. Add
   `iterations>=N` to cap runaway loops.
6. **Run it.** `infini run ./Loopfile`. Look at the trace. Iterate.

The [`examples/`](../../examples/) directory has three runnable demos
that follow this structure.

---

## The discipline, not the tool

Loop Engineering is a discipline, not a tool. INFINI is the tool that
enforces the discipline. If you use INFINI without the discipline, you
get loops that pass verification but ship bad work. If you use the
discipline without INFINI, you get the right behavior but no portability.

You need both. This handbook is the discipline; INFINI is the tool.

---

## What's next

- Chapter 4, [Verification](verification.md) — the heart of the discipline.
- Chapter 7, [Replay](replay.md) — how to debug loops.
- The canonical prompt: [`prompts/loop-engineer.md`](../../prompts/loop-engineer.md).
