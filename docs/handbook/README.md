# The INFINI Handbook

A book-length guide to the discipline of Loop Engineering. Written to be
read in order, but each chapter stands alone.

> The spec lives in [`spec/`](../../spec/). The Loop Engineer prompt lives
> in [`prompts/loop-engineer.md`](../../prompts/loop-engineer.md). This
> handbook is the *teaching* — how to think like a Loop Engineer.

---

## Chapters

1. [Why Loopfiles?](why-loopfiles.md) — the problem and the bet.
2. [Design Philosophy](design-philosophy.md) — what INFINI is and isn't.
3. [Loop Engineering](loop-engineering.md) — the discipline.
4. [Verification](verification.md) — the heart of the discipline.
5. [Memory](memory.md) — loops that learn.
6. [Observability](observability.md) — loops you can see.
7. [Replay](replay.md) — loops you can debug.
8. [Governance](governance.md) — loops you can trust.
9. [Portability](portability.md) — loops that survive engine swaps.
10. [Standards](standards.md) — why this is a standard, not a tool.

---

## How to read this handbook

- **New to INFINI?** Read chapters 1–3 in order. They explain what INFINI
  is and why it exists.
- **Writing your first Loopfile?** Read chapter 3, then chapters 4 and 7.
  Verification and replay are the two things that make a loop a loop.
- **Building an adapter?** Read chapters 6 and 9, then
  [`sdk/`](../../sdk/).
- **Evaluating INFINI for your team?** Read chapters 1, 8, and 10. They
  explain the bets and the trade-offs.

---

## What this handbook is not

- **Not a tutorial.** Tutorials live in [`examples/`](../../examples/).
- **Not a spec.** The normative spec lives in
  [`spec/loopfile-v1.md`](../../spec/loopfile-v1.md).
- **Not a reference.** Reference docs live in [`sdk/`](../../sdk/) and
  [`cli/`](../../cli/).
- **Not marketing.** This handbook makes bets and acknowledges trade-offs.
  It does not promise INFINI will win.

---

## License

CC-BY-4.0. See [repository LICENSE](../../LICENSE).
