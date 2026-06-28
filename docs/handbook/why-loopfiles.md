# Why Loopfiles?

Chapter 1 of the [INFINI Handbook](README.md).

---

## The problem

Most agent systems today are **chains**: a fixed sequence of prompts,
executed once, with a human at the end deciding whether the output is good
enough.

Chains are scripts. Scripts don't ship production software. Scripts don't
learn. Scripts break silently when the world changes underneath them.

The industry has built increasingly elaborate chains and called them
"agents." They are not agents. They are pipelines with a chat interface.

A real agent is a system that **loops**:

1. **Observe** — read state, read the world.
2. **Plan** — decide what to do next.
3. **Execute** — do it.
4. **Verify** — check whether what it did was correct.
5. **Critique** — if it was wrong, say *why*.
6. **Improve** — try again, better.

A loop without verification is a hallucination factory. A loop without
critique is a sycophant. A loop without improvement is a stuck record. All
three are required.

---

## Why loops are hard

The reason most "agent" systems are chains is that loops are hard.

A chain is easy to write: you put prompts in a file, you run them in
order, you look at the output. If it's wrong, you tweak a prompt and run
it again. Repeat until it works.

A loop is harder:

- You have to **declare** what "done" means, because the loop decides on
  its own whether to iterate.
- You have to **bound** the cost, because a stuck loop spends money
  forever.
- You have to **verify** the output, because the loop doesn't know when
  to stop.
- You have to **persist state**, because you want to debug the loop, not
  just rerun it.
- You have to **learn** from each iteration, because otherwise the loop
  repeats the same mistake.

Every team that ships agents in production eventually rediscovers these
requirements. They write them, ad hoc, in their framework of choice. Then
they switch frameworks and write them again. And again.

---

## The bet

INFINI makes four bets:

1. **Engines will keep multiplying.** LangGraph today, something else
   tomorrow. Pinning your workflow to one runtime is a mistake.
2. **Models will keep getting cheaper.** The cost of running a 6-iteration
   loop today is the cost of running a 1-iteration chain in two years.
   Loops get cheaper over time; chains don't get smarter.
3. **Verification will become the bottleneck.** Once generation is cheap,
   the question is no longer "can the model do it?" but "how do we know
   it's right?" Verification is the discipline. Loops make verification
   first-class.
4. **Portability wins.** Docker proved this for containers. Terraform
   proved it for infrastructure. OpenAPI proved it for APIs. The agent
   ecosystem has not yet had its portable-format moment. INFINI is that
   moment.

---

## What a Loopfile is

A Loopfile is a portable, declarative description of an agent loop. It
declares *what* the loop is trying to do, *how* to verify it succeeded,
*how much* it's allowed to cost, and *when* to stop. It does not declare
*how* the model reasons — that's the engine's job.

```yaml
LOOPFILE: "1.0"
name: dark-mode-toggle
OBJECTIVE: "Add a dark mode toggle, preserve tests"
BUDGET: { dollars: 5, minutes: 15 }
VERIFY:
  syntactic: ["tests:pass", "lint"]
  semantic:  ["rubric:90"]
STOP_WHEN: ["all_verify_passed"]
```

A Loopfile is to an agent loop what a Dockerfile is to a container: a
portable artifact that any conforming runtime can execute.

---

## What a Loopfile is not

- **Not a workflow.** Workflows are scripted; loops are autonomous. Both
  belong; they're different things.
- **Not a prompt.** A prompt is part of a step; a Loopfile is the whole
  loop.
- **Not a framework.** Frameworks lock you in. Standards don't.
- **Not a model.** Loopfiles are model-agnostic. `model_tier` is
  engine-resolved.
- **Not a company.** The spec is CC-BY-4.0. The code is MIT. The registry
  is open.

---

## The lineage

```
Docker      standardized containers.
Terraform   standardized infrastructure.
OpenAPI     standardized APIs.
Markdown    standardized documents.
Git         standardized collaboration.
INFINI      standardizes autonomous work.
```

Each of these won by being *boring*, *portable*, and *open*. INFINI
intends to be the same.

---

## What's next

- Chapter 2, [Design Philosophy](design-philosophy.md), explains what
  INFINI is and isn't, and what we're not optimizing for.
- Chapter 3, [Loop Engineering](loop-engineering.md), introduces the
  discipline.
- Or skip ahead to [`examples/`](../../examples/) to see a Loopfile in
  action.
