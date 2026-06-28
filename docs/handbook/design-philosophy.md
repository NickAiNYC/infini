# Design Philosophy

Chapter 2 of the [INFINI Handbook](README.md).

---

## What INFINI is

INFINI is four things:

1. **A format** — the Loopfile.
2. **A spec** — what conformance means.
3. **A registry** — where Loopfiles live.
4. **A discipline** — the Loop Engineer role.

Each of these exists for a reason. None of them is incidental.

### The format

The Loopfile is a YAML document. YAML, not JSON, because loops are
written by humans and YAML supports comments. The format is declarative:
you describe *what* the loop does, not *how* the engine should do it.

### The spec

The spec is the contract. It says what a v1.0 Loopfile can express and
what an engine must do to be conformant. Without the spec, the format is
just a convention; with the spec, it's a standard.

### The registry

The registry makes Loopfiles shareable. Without it, teams copy-paste YAML
between repos and lose track of versions. With it, a Loopfile is an
addressable, signed, immutable artifact.

### The discipline

The Loop Engineer role is what makes loops different from chains. The
discipline will exist whether INFINI names it or not. Naming it early
gives it a home. See [`prompts/loop-engineer.md`](../../prompts/loop-engineer.md).

---

## What INFINI is not

### INFINI is not a runtime

We don't ship an agent executor. We ship a reference engine that conforms
to the spec. Other engines (Hermes, OpenClaw, LangGraph, etc.) conform to
the same spec and run the same Loopfiles.

This is the Docker move: the engine got commoditized; the format ate the
world.

### INFINI is not a framework

Frameworks lock you in. They have opinions about how agents should
reason, what tools they should use, how state should be shaped. INFINI
has opinions about *loops* — not about agents.

If your framework wants to support Loopfiles, write an adapter. Your
framework's opinions stay intact; INFINI adds portability on top.

### INFINI is not a model

Loopfiles declare `model_tier`, not model names. The engine resolves
`model_tier: sonnet` to whatever "sonnet" means today. This keeps
Loopfiles portable across model providers and across model generations.

When Claude 4 ships, your Loopfiles don't change. When GPT-5 ships, your
Loopfiles don't change. The engine's model resolution changes; the
Loopfile doesn't.

### INFINI is not a company

The spec is CC-BY-4.0. The code is MIT. The registry is open. Anyone can
implement any part of INFINI without permission, payment, or attribution
(beyond the license terms).

This is intentional. Standards that are owned by companies get captured
by companies. INFINI intends to be owned by the ecosystem.

---

## What we are not optimizing for

### Raw throughput

If you need to run 10 million inferences per second, INFINI is not for
you. INFINI optimizes for *correctness* and *inspectability*, not
throughput. Loops have overhead — state persistence, trace emission,
verification. That overhead is the point.

### Single-engine workflows

If you're committed to one runtime forever, you don't need a portable
format. INFINI is for teams who expect to swap engines — once, twice, or
many times. The cost of writing a Loopfile is paid back the first time
you swap engines without rewriting your loops.

### Vibe coding

INFINI loops must declare their verification criteria up front. If you
don't know what "done" looks like, INFINI can't help you. (It can help
you *figure out* what "done" looks like — that's the planner's job — but
it won't ship unverified work.)

This is a feature, not a limitation. The discipline of declaring
verification is what turns a vibe coder into a Loop Engineer.

### Marketing

INFINI does not exaggerate adoption, fake telemetry, fake contributors,
fake stars, or fake benchmarks. The repo's star count is real. The
compatibility matrix reflects real, tested conformance. If a feature is
preview, it's labeled preview. If a feature is planned, it's labeled
planned.

This is also intentional. Standards gain trust by being honest about
their state. Inflating numbers gains short-term attention at the cost of
long-term credibility.

---

## The bets, restated

1. Engines will keep multiplying.
2. Models will keep getting cheaper.
3. Verification will become the bottleneck.
4. Portability wins.

Every design decision in INFINI flows from these four bets. If you
disagree with one of them, you'll disagree with parts of INFINI. That's
fine — INFINI is not for everyone.

---

## What's next

- Chapter 3, [Loop Engineering](loop-engineering.md), introduces the
  discipline that the rest of the handbook explores.
- For the normative spec, see [`spec/loopfile-v1.md`](../../spec/loopfile-v1.md).
- For the design patterns that follow from this philosophy, see
  [`docs/patterns/`](../patterns/).
