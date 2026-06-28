# MANIFESTO

> **Loops > Chains.**

---

## The problem

Most agent systems today are **chains**: a fixed sequence of prompts, executed once, with a human at the end deciding whether the output is good enough.

Chains are scripts. Scripts don't ship production software. Scripts don't learn. Scripts break silently when the world changes underneath them.

The industry has built increasingly elaborate chains and called them "agents." They are not agents. They are pipelines with a chat interface.

---

## The claim

An **agent** is a system that **loops**:

1. **Observe** — read state, read the world.
2. **Plan** — decide what to do next.
3. **Execute** — do it.
4. **Verify** — check whether what it did was correct.
5. **Critique** — if it was wrong, say *why*.
6. **Improve** — try again, better.

A loop without verification is a hallucination factory. A loop without critique is a sycophant. A loop without improvement is a stuck record. **All three are required.**

---

## The bet

We bet that:

1. **Engines will keep multiplying.** LangGraph today, something else tomorrow. Pinning your workflow to one runtime is a mistake.
2. **Models will keep getting cheaper.** The cost of running a 6-iteration loop today is the cost of running a 1-iteration chain in two years. Loops get cheaper over time; chains don't get smarter.
3. **Verification will become the bottleneck.** Once generation is cheap, the question is no longer "can the model do it?" but "how do we know it's right?" Verification is the discipline. Loops make verification first-class.
4. **Portability wins.** Docker proved this for containers. Terraform proved it for infrastructure. OpenAPI proved it for APIs. The agent ecosystem has not yet had its portable-format moment. INFINI is that moment.

---

## What INFINI is

INFINI is the **Loopfile**: a portable, declarative description of an agent loop. It declares *what* the loop is trying to do, *how* to verify it succeeded, *how much* it's allowed to cost, and *when* to stop. It does not declare *how* the model reasons — that's the engine's job.

INFINI is not:

- a runtime. We don't ship an agent executor. We ship a reference engine that conforms to the spec.
- a framework. Frameworks lock you in. Standards don't.
- a model. We are model-agnostic by design. `model_tier` is engine-resolved.
- a company. The spec is CC-BY-4.0. The code is MIT. The registry is open.

INFINI is:

- a **format** — the Loopfile.
- a **spec** — what conformance means.
- a **registry** — where Loopfiles live.
- a **discipline** — the Loop Engineer role.

---

## What we are not optimizing for

- **Raw throughput.** If you need to run 10 million inferences per second, INFINI is not for you. INFINI optimizes for *correctness* and *inspectability*, not throughput.
- **Single-engine workflows.** If you're committed to one runtime forever, you don't need a portable format. INFINI is for teams who expect to swap engines — once, twice, or many times.
- **Vibe coding.** INFINI loops must declare their verification criteria up front. If you don't know what "done" looks like, INFINI can't help you. (It can help you *figure out* what "done" looks like — that's the planner's job — but it won't ship unverified work.)

---

## The discipline

A **Loop Engineer** is someone who:

- refuses to ship unverified loops,
- escalates precisely — not too early, not too late,
- treats every run as a learning opportunity,
- writes loops that other engines can run without modification,
- debugs loops with `infini inspect` and `infini replay`, not with `print` statements,
- benchmarks loops on cost, runtime, and verification rate — and publishes the results.

This role will exist whether INFINI names it or not. We're naming it early so the discipline has a home.

📖 **Read the canonical prompt:** [`prompts/loop-engineer.md`](prompts/loop-engineer.md)

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

Each of these won by being *boring*, *portable*, and *open*. INFINI intends to be the same.

---

## What you can do

- **Write a Loopfile** for one of your recurring agent workflows.
- **Run it** with the INFINI Reference Engine, Hermes, or OpenClaw.
- **Inspect the trace**. If it's not inspectable, it's not a loop.
- **Publish it** to the registry.
- **Improve it** until verification passes consistently.
- **Open an RFC** if the spec is missing something you need.

We are shipping first. Join us.

**Loops that don't end. Loops that improve.**
