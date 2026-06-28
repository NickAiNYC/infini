# Prompt Soup

## Smell

The Loopfile is one giant step with a 2000-word prompt. There's no
`STEPS` decomposition; there's just one `execute` step that does
everything.

## Why it fails

Prompt soup is a chain, not a loop. You can't verify intermediate
output, you can't replay from a specific point, and you can't tell which
part of the prompt caused the failure.

It's also non-portable. The prompt has engine-specific assumptions baked
in ("use the LangGraph tool-calling convention"). The Loopfile runs on
one engine, badly.

## Fix

- **Decompose.** If your prompt has more than 200 words, it's probably
  doing more than one thing. Split it into steps.
- **Each step does one thing.** "Plan," "edit," "test," "open PR" are
  steps. "Do the whole task" is not.
- **Use `OBJECTIVE` for the high-level goal.** The objective is one
  sentence. Steps implement the objective; they don't restate it.
- **Move domain knowledge into `LESSONS`.** If your prompt has
  boilerplate ("always use the team's coding standards"), put it in the
  lessons file. Future runs read it automatically.
- **Inspect the trace.** If `infini inspect` shows one step that
  consumed 80% of the budget, you have prompt soup. Split that step.
- **Use [Planning Loop](../patterns/planning-loop.md).** A separate
  `plan` step that produces a structured plan, then `execute` steps
  that implement each part of the plan. This is the antidote to prompt
  soup.
