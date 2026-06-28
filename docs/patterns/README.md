# Loop Design Patterns

Design patterns for Loop Engineering. Each pattern has:

- **Problem** — when this pattern applies.
- **Diagram** — the shape of the loop.
- **Loopfile** — a minimal example.
- **Tradeoffs** — what this pattern costs and what it gives.
- **Best practices** — how to use it well.

> Patterns are not laws. They're defaults. Break them when you have a
> reason; know the reason.

---

## The patterns

| Pattern | What it's for |
| --- | --- |
| [Retry](retry.md) | Re-running a step that failed transiently. |
| [Human Approval](human-approval.md) | Pausing for human review before an irreversible step. |
| [Budget Guard](budget-guard.md) | Stopping before the budget is exhausted. |
| [Parallel Workers](parallel-workers.md) | Running multiple steps concurrently. |
| [Fan Out](fan-out.md) | Splitting one input into many parallel sub-tasks. |
| [Fan In](fan-in.md) | Combining many parallel outputs into one. |
| [Verification Gate](verification-gate.md) | A step that verifies the previous step's output. |
| [Reflection Loop](reflection-loop.md) | A step that critiques the previous step's output. |
| [Research Loop](research-loop.md) | Multi-source research with citations. |
| [Planning Loop](planning-loop.md) | Plan-then-execute. |
| [Memory Update](memory-update.md) | Appending a lesson after a run. |
| [Escalation](escalation.md) | Handing off to a human when confidence is low. |
| [Self Improvement](self-improvement.md) | A loop that rewrites its own Loopfile. |

---

## How to read a pattern

Start with the **Problem**. If your problem matches, read the **Diagram**
and **Loopfile**. Then read the **Tradeoffs** — every pattern has a cost.
Finally, read the **Best practices** — they save you from common mistakes.

---

## Anti-patterns

For what *not* to do, see [`docs/anti-patterns/`](../anti-patterns/).

---

## License

CC-BY-4.0. See [repository LICENSE](../../LICENSE).
