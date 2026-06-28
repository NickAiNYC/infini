# Loop Anti-Patterns

What *not* to do, and why. Each anti-pattern has:

- **Smell** — how to recognize it.
- **Why it fails** — the failure mode.
- **Fix** — what to do instead.

> Anti-patterns are not forbidden. They're warnings. If you find yourself
> in one, know why you're there.

---

## The anti-patterns

| Anti-pattern | What goes wrong |
| --- | --- |
| [Infinite Loops](infinite-loops.md) | The loop never stops. |
| [Hallucination Chains](hallucination-chains.md) | Each iteration builds on the previous one's hallucinations. |
| [Missing Verification](missing-verification.md) | A loop with no `VERIFY` block. |
| [Unbounded Costs](unbounded-costs.md) | A loop with no `BUDGET`. |
| [Hidden State](hidden-state.md) | State the engine doesn't know about. |
| [Tool Spam](tool-spam.md) | The loop calls tools compulsively without progress. |
| [Prompt Soup](prompt-soup.md) | A Loopfile that's actually a prompt, not a loop. |
| [Over-Planning](over-planning.md) | The plan step costs more than the execution. |
| [No Exit Condition](no-exit-condition.md) | `STOP_WHEN` doesn't actually stop. |

---

## How to read an anti-pattern

Start with the **Smell**. If your loop smells like this, read **Why it
fails** to understand the failure mode. Then read **Fix** to get out of
it.

---

## License

CC-BY-4.0. See [repository LICENSE](../../LICENSE).
