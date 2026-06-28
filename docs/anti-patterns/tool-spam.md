# Tool Spam

## Smell

The loop calls tools compulsively — 50 browser navigations per step, 20
terminal runs per verification, repeated GitHub API calls for the same
resource. The trace is a wall of tool calls, most of which produced
nothing useful.

## Why it fails

Tool spam wastes budget. Each tool call costs tokens (for the model to
decide to call it) and time (for the tool to run). A loop that calls 50
tools per step burns through its budget without making progress.

It also makes the trace unreadable. `infini inspect` shows a wall of
tool calls; finding the one that mattered is a needle in a haystack.

## Fix

- **Cap tool calls per step.** Most adapters support a `max_tool_calls`
  config. Set it to 10. If a step needs more, split the step.
- **Cache tool results.** If step B needs the same GitHub PR that step A
  fetched, step B should read A's cached result, not re-fetch.
- **Inspect the trace.** If you see 50 tool calls in one step, that's
  tool spam. Look at what each call returned; most will be duplicates or
  no-ops.
- **Tighten the prompt.** Tool spam is often a prompt problem. The model
  doesn't know what it has, so it keeps fetching. Tell it explicitly:
  "You have X. Don't re-fetch."
- **Use [Verification Gate](../patterns/verification-gate.md).** A gate
  after every N tool calls catches spam early. If the gate fails, the
  step retries with a tighter prompt.
- **Use cheaper model tiers for tool-heavy steps.** A `haiku`-tier model
  that calls 5 tools is cheaper than a `sonnet`-tier model that calls
  50.
