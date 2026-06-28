# Missing Verification

## Smell

The Loopfile has no `VERIFY` block, or has one that's trivially
satisfied (`"output.md:exists"`).

## Why it fails

A loop without verification is not a loop — it's a chain that happens to
repeat. The model says it's done, so it must be done. There's no check.

This is the single most common anti-pattern. It feels productive (the
loop "ships" every time) and it's catastrophically wrong (the loop ships
garbage every time).

## Fix

- **Every Loopfile must have a `VERIFY` block.** This is enforced by
  `infini validate`. If you can't write a `VERIFY` block, you don't have
  a loop yet — you have a vibe.
- **Have at least one semantic check.** `judge:correctness>=85` is a
  starting point. Tune it from there.
- **Don't write trivial syntactic checks.** `"output.md:exists"` is
  trivially satisfied by an empty file. Use `"output.md:non_empty"` or,
  better, `"output.md:word_count_in_range"`.
- **Verify the verifier.** A verifier that always passes is worse than
  no verifier. Run `infini inspect` on a verified run; would you have
  shipped this work? If not, your verifier is too lenient.
- **Read [Chapter 4 of the Handbook](../handbook/verification.md).**
  Verification is the heart of Loop Engineering. Don't skip it.
