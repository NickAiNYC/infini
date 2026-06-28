# Hallucination Chains

## Smell

Each iteration builds on the previous one's hallucinations. The loop
gets more confident and more wrong at the same time.

## Why it fails

The loop has no external ground truth. Each iteration reads the previous
iteration's output as input. The model, asked to improve on its own
output, doubles down on its own mistakes. By iteration 5, the output is
a tower of unverified claims, each one slightly more confident than the
last.

This is the agent equivalent of a circular citation: source A cites
source B, source B cites source A, and both are wrong.

## Fix

- **Bring in external evidence every iteration.** The loop should not
  read its own output as its primary input. It should read the world
  (a repo, a database, a web page) every iteration.
- **Use a separate verifier.** The verifier should not be the same agent
  as the builder. Same-model verifiers tend to confirm what the builder
  produced.
- **Cite sources.** Every claim in the output should be traceable to an
  external source. The [Research Loop](../patterns/research-loop.md)
  pattern enforces this with `every_claim_has_citation`.
- **Inspect the trace.** If iteration 5's output cites iteration 4's
  output as evidence, you have a hallucination chain. Break it.
- **Use [Reflection Loop](../patterns/reflection-loop.md) with a
  different model tier.** An `opus` critic reviewing a `sonnet` draft
  catches hallucinations the drafter can't see in itself.
