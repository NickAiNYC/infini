# Standards

Chapter 10 of the [INFINI Handbook](README.md).

> INFINI is a standard, not a tool. The distinction matters.

---

## Tools vs. standards

A **tool** is something you use. A **standard** is something you agree
on. Tools compete; standards coordinate.

Docker the tool is a container runtime. Dockerfile the standard is what
made containers portable. The tool could have lost to rkt or LXC; the
standard won because it was open and any runtime could implement it.

Terraform the tool is an IaC runner. HCL + the provider protocol the
standard is what made infrastructure portable. The tool competes with
Pulumi and Crossplane; the standard is what makes them all speak to the
same clouds.

INFINI the tool is a CLI and a reference engine. Loopfile the standard is
what makes agent loops portable. The tool could lose to LangGraph or
CrewAI; the standard is what would make them all speak the same loop
format.

We are building the standard. The tool exists to make the standard
concrete.

---

## What makes a standard win

Looking at the standards that won — Dockerfile, HCL, OpenAPI, Markdown,
Git — they share five properties:

1. **Boring.** The format is simple enough that a human can read and
   write it. Dockerfile is YAML-ish; HCL is JSON-ish; Markdown is plain
   text. None of them require a PhD to author.
2. **Portable.** The format doesn't favor one implementation. A Dockerfile
   runs on Docker, Podman, containerd, and runc. An OpenAPI spec generates
   clients in 40 languages.
3. **Open.** The spec is licensed to be implemented by anyone, including
   competitors. Dockerfile is not owned by Docker; OpenAPI is not owned
   by any one company.
4. **Minimal.** The format declares intent, not implementation. A
   Dockerfile says "install nginx"; it doesn't say "run `apt-get install
   nginx` on Ubuntu 22.04 with these specific flags." The implementation
   decides the flags.
5. **Tool-rich.** The standard spawns an ecosystem of tools. Dockerfile
   had docker, docker-compose, buildkit, kaniko, dive, hadolint. The
   tools make the standard more useful; the standard makes the tools
   interoperable.

INFINI aims for all five. The Loopfile is YAML (boring). It runs on any
conforming engine (portable). The spec is CC-BY-4.0 (open). It declares
intent, not implementation (minimal). The CLI, the Observatory, the
registry, the adapters, the canonical loops, the marketplace, the SDK —
these are the tools (tool-rich).

---

## What makes a standard lose

Standards lose when they:

1. **Favor one implementation.** The format bakes in assumptions from one
   tool, and other tools can't conform. (Many "standards" in the agent
   space today have this problem.)
2. **Grow too fast.** The format adds features faster than implementers
   can keep up. Conformance becomes a moving target; engines stop trying.
3. **Get captured.** A company owns the standard and uses it to extract
   rent. Implementers fork or leave.
4. **Lack tooling.** The standard exists on paper but no one builds tools
   for it. Users pick a different standard that has tools.
5. **Solve the wrong problem.** The standard is elegant but doesn't
   address a real pain. No one adopts it.

INFINI's defenses against each:

1. **Favor one implementation.** The reference engine is the canonical
   impl, but it conforms to the same spec as everyone else. No special
   privileges.
2. **Grow too fast.** Spec changes go through RFCs with two-week minimum
   review. Minor versions are additive. Major versions are rare.
3. **Get captured.** The spec is CC-BY-4.0. The code is MIT. The roadmap
   explicitly says no "INFINI Pro" or "INFINI Enterprise." The project
   intends to move to a foundation post-1.0.
4. **Lack tooling.** The CLI, Observatory, registry, adapters, and SDK
   ship with the spec. Tools exist on day one.
5. **Solve the wrong problem.** The problem — "agent workflows are
   non-portable across runtimes" — is real and widely felt. Every team
   that's tried to switch agent frameworks has hit it.

---

## The lineage, restated

```
Docker      standardized containers.
Terraform   standardized infrastructure.
OpenAPI     standardized APIs.
Markdown    standardized documents.
Git         standardized collaboration.
INFINI      standardizes autonomous work.
```

Each of these named a category, then owned it through a portable format
that any tool could implement. INFINI does the same for autonomous agent
loops.

The bet is simple. Engines will keep multiplying. Models will keep
getting cheaper. What won't multiply is the *patience* of teams who want
their agent workflows to be reproducible, auditable, and engine-agnostic.
Whoever owns the portable format owns the category.

---

## What's next

You've reached the end of the handbook. Where to go from here:

- **Write your first Loopfile.** Start with
  [`examples/`](../../examples/).
- **Read the spec.** [`spec/loopfile-v1.md`](../../spec/loopfile-v1.md).
- **Read the RFCs.** [`spec/rfcs/`](../../spec/rfcs/).
- **Run a demo.** [`examples/hybrid-hermes-openclaw/`](../../examples/hybrid-hermes-openclaw/).
- **Open an RFC.** [`spec/rfcs/README.md`](../../spec/rfcs/README.md).
- **List yourself as an adopter.** [`docs/adopters.md`](../adopters.md).

The standard exists. The tools exist. The discipline exists. The rest is
adoption.

We are shipping first. Join us.
