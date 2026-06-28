# The INFINI Handbook

A book-length guide to the discipline of Loop Engineering. Written to be
read in order, but each chapter stands alone and cross-links to the
others.

> The spec lives in [`spec/`](../../spec/). The Loop Engineer prompt
> lives in [`prompts/loop-engineer.md`](../../prompts/loop-engineer.md).
> This handbook is the *teaching* — how to think like a Loop Engineer.

---

## Chapters

### Getting Started

1. [Why Loopfiles?](why-loopfiles.md) — the problem and the bet.
2. [Design Philosophy](design-philosophy.md) — what INFINI is and isn't.
3. [Loop Engineering](loop-engineering.md) — the discipline.

### Core Concepts

4. [Verification](verification.md) — the heart of the discipline.
5. [Memory](memory.md) — loops that learn.
6. [Observability](observability.md) — loops you can see.
7. [Replay](replay.md) — loops you can debug.

### Architecture

8. [Governance](governance.md) — loops you can trust.
9. [Portability](portability.md) — loops that survive engine swaps.

### Advanced

10. [Standards](standards.md) — why this is a standard, not a tool.
11. [MCP Roadmap](mcp-roadmap.md) — native Model Context Protocol support.
12. [Adapter Development](adapter-development.md) — build your own adapter.
13. [Certification](certification.md) — get your adapter certified.

### Ecosystem

14. [Marketplace](marketplace.md) — browse and publish loops.
15. [Community](community.md) — contribute, discuss, govern.

### Reference

16. [Getting Started Guide](getting-started.md) — 15-minute on-ramp.
17. [Architecture](architecture.md) — the full system diagram.

---

## How to read this handbook

- **New to INFINI?** Read [Getting Started](getting-started.md), then
  chapters 1–3.
- **Writing your first Loopfile?** Read chapter 3, then chapters 4 and 7.
- **Building an adapter?** Read chapters 12 and 13, then the
  [Adapter SDK](../../sdk/).
- **Evaluating INFINI for your team?** Read chapters 1, 8, and 10.

Every chapter cross-links to related chapters and to the normative spec.
No duplicated explanations — each concept is defined once and referenced
everywhere else.

---

## Cross-reference map

| If you want to... | Read this |
| --- | --- |
| Understand why INFINI exists | [Why Loopfiles?](why-loopfiles.md) |
| Write your first Loopfile | [Getting Started](getting-started.md) |
| Add verification to a loop | [Verification](verification.md) |
| Debug a failed run | [Replay](replay.md) |
| See what happened in a run | [Observability](observability.md) |
| Make a loop remember across runs | [Memory](memory.md) |
| Add governance to a loop | [Governance](governance.md) |
| Switch engines without rewriting | [Portability](portability.md) |
| Add MCP tools to a loop | [MCP Roadmap](mcp-roadmap.md) |
| Build an adapter | [Adapter Development](adapter-development.md) |
| Certify an adapter | [Certification](certification.md) |
| Publish a loop | [Marketplace](marketplace.md) |
| Contribute to the project | [Community](community.md) |
| Understand the full architecture | [Architecture](architecture.md) |

---

## What this handbook is not

- **Not a tutorial.** Tutorials live in [`examples/`](../../examples/).
- **Not a spec.** The normative spec lives in
  [`spec/loopfile-v1.md`](../../spec/loopfile-v1.md).
- **Not a reference.** Reference docs live in [`sdk/`](../../sdk/) and
  [`cli/`](../../cli/).
- **Not marketing.** This handbook makes bets and acknowledges trade-offs.

---

## License

CC-BY-4.0. See [repository LICENSE](../../LICENSE).
