# refactor-loop — essay

> *Draft. PRs welcome.*

Refactoring is the loop where verification matters most. The behavior diff isn't optional; if you can't prove the behavior didn't change, you didn't refactor — you rewrote.

## The VERIFY block is the loop

Most teams write loops that look like this one but skip the VERIFY block. Without verification, you don't have a loop — you have a chain that happens to repeat. The discipline lives in declaring, up front, what counts as "done" and how you'll check it.

## When this loop fails

The most common failure mode is a verifier that's too lenient. A `judge:quality>=85` check that always returns 90 is worse than no check at all — it gives false confidence. Tune your verifiers against real failures.

## Composition

This loop can be composed with other canonical loops. For example, a `coding-loop` can call a `test-gen-loop` as a sub-step, or a `debug-loop` can call a `review-loop` to vet the proposed fix. See [RFC-0004](../../spec/) (planned) for the composition protocol.

## License

MIT. See [repository LICENSE](../../LICENSE).
