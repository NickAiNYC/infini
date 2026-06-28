# Manifesto: Loops > Chains

> Chains are scripts. DAGs are pipelines. **Loops are systems.**
> Stop building chains. Start engineering loops.

---

## The State of Agents Today

The agent ecosystem in 2026 has 100 frameworks and zero standards.

LangGraph. CrewAI. AutoGen. OpenClaw. HermesAgents. SmolAgents. Mastra. Bee. Every week another runtime. Every runtime reinvents the same five primitives:

- State management
- Resume after crash
- Verification
- Cost ceilings
- Self-improvement

Every team rebuilds them. Every team gets them slightly wrong. Every loop is non-portable. A graph written for LangGraph is useless in CrewAI. A crew written for CrewAI cannot run on OpenClaw. The ecosystem fragments instead of compounds.

This is not a tooling problem. This is a **format problem**.

---

## The Analogy That Explains Everything

In 2013, there were a dozen container runtimes: LXC, OpenVZ, rkt, Docker, systemd-nspawn. Each had its own image format. None interoperated. Containers were a niche experiment.

Docker did not win because Docker Engine was the best runtime. Docker won because of **three things**:

1. **Dockerfile** — a portable, declarative format anyone could read and write
2. **Registry** — a place to publish, version, and pull images
3. **Hub** — a curated catalog with stars, downloads, and trust signals

The engine got commoditized. The format ate the world.

The agent ecosystem is in 2013. We have runtimes. We don't have a format.

---

## The Three Tiers of AI Work

Most teams are stuck at Tier 1. Some reach Tier 2. Almost no one is at Tier 3.

### Tier 1 — The Prompt (a wish)
You write a prompt. You paste it into ChatGPT. You get an answer. You use it. Next time, you write the prompt again. Nothing persists. Nothing improves. Every run is groundhog day.

This is fine for one-off questions. It is broken for anything that runs twice.

### Tier 2 — The Chain (a script)
You string prompts together. Output of step 1 feeds step 2. Maybe you cache results. Maybe you add a retry. This is LangChain's basic unit. It is a script. It runs once, top to bottom, and forgets.

Chains are fine for pipelines. They are broken for agents, because agents need feedback. A chain that fails at step 5 has no way to revise step 3. It just crashes.

### Tier 3 — The Loop (a system)
A loop has:
- **State** — what happened, what's next, what's blocked
- **Feedback** — observations flow back into decisions
- **Verification** — the loop checks its own output before declaring done
- **Resume** — interruption is recoverable, not fatal
- **Self-improvement** — every run makes the next run better

Loops are how production systems actually work. Your CI is a loop. Your deploy pipeline is a loop. Your on-call rotation is a loop. Your SRE practice is a loop. Anything that runs unattended for years is a loop.

The agent ecosystem talks about agents. It builds chains. It ships prompts. **It almost never builds loops.**

---

## The Loop Engineer's Law

Any AI system that runs more than once must have:

1. A durable state file
2. A resume protocol
3. At least 2 verification tiers
4. A cost ceiling
5. A self-improvement hook

If any of these is missing, it is not production-ready.

This is not opinion. This is operational hygiene borrowed from every other discipline that runs software unattended:

- CI/CD has artifacts, retries, gates, and post-mortems
- SRE has runbooks, SLOs, incident reports, and postmortems
- Data pipelines have checkpoints, schemas, and observability
- ML pipelines have model registries, eval suites, and drift monitors

Agents should have all of the above. Today they have none of it.

---

## Why Loops Ship and Chains Don't

A chain is a one-shot bet. You write it, you run it, you hope. If it fails, you debug from scratch. If it succeeds, you have no idea why. If you run it again next week, you start over.

A loop is a compounding asset. Every run produces:

- A trace you can replay
- A cost report you can audit
- A failure analysis you can learn from
- A version bump you can rollback to
- A lessons file the next run inherits

After 100 runs, a chain is still a chain. After 100 runs, a loop is a tuned, documented, audited production system that can be handed to a new engineer in an afternoon.

---

## The Cultural Problem

The reason we have 100 frameworks and zero standards is cultural. Frameworks are resume-building. Standards are governance-building. Open source rewards the former; the industry needs the latter.

Every framework author wants to own the runtime. No one wants to own the format. Owning the format is slow, unglamorous work: writing specs, running RFCs, maintaining a registry, curating examples. It is also the only thing that compounds.

We are asking the wrong question. The question is not "which agent framework is best?" The question is "what can I write once and run on any framework?"

The answer is: **a Loopfile.**

---

## What We Are Building

Loom is the format, not the runtime.

- **Loopfile** — a runtime-agnostic declaration of an agentic loop
- **loom registry** — a place to publish, version, and pull loops
- **loom inspect** — visualize any run trace, any engine
- **loom replay** — time-travel debug through every decision
- **loom diff** — semantic changelogs between loop versions
- **loom ci** — GitHub Action that runs your loops on every PR
- **loom/anthology** — 12 canonical loops with essays and benchmarks

We do not ship an engine. We ship the format the engines agree on.

If you write a Loopfile, it should run on LangGraph today, CrewAI tomorrow, and whatever comes next year. Your loop is portable. Your investment compounds.

---

## The Ask

If you build agents:

1. Write your next loop as a Loopfile. Not as a Python script. Not as a LangGraph graph. As a Loopfile.
2. Publish it to the registry. Even if it's bad. Especially if it's bad — that's how we learn what the spec is missing.
3. Run `loom inspect` on your traces. Show your team. Show your recruiter. Show your HN comment.
4. When you find a gap in the spec, open an RFC. We will merge the good ones.

If you build a runtime:

1. Add a `loom` adapter. Let your users run Loopfiles.
2. Publish your engine manifest. Let users filter the registry by what you support.
3. Contribute your verification primitives back as standard check names.

If you hire engineers:

1. Look for "Loop Engineer" on resumes. It's the role that ships agents to prod.
2. Ask candidates to write a Loopfile for a real problem in your interview.
3. Pay people who can do this. They are rare.

---

## Closing

Chains are scripts. DAGs are pipelines. Loops are systems.

The team that owns the loop format owns the next decade of agentic AI. The team that owns the loop format is whoever ships first, ships openly, and ships with humility.

We are shipping first.

**Loops that ship. Loops that learn.**
