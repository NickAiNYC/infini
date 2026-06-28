# INFINI RFC Process

INFINI uses Requests for Comments (RFCs) to propose changes to the Loopfile
spec, the registry protocol, and the adapter interface. The process is
modeled on [Rust's RFC process](https://github.com/rust-lang/rfcs),
[Kubernetes KEPs](https://github.com/kubernetes/enhancements), and
[Python PEPs](https://peps.python.org).

This document describes how RFCs work.

---

## When to open an RFC

Open an RFC when you want to change:

- **The Loopfile spec** — any change to what a Loopfile can express or what conformance means.
- **The registry protocol** — any change to the endpoints, addressing, or signing scheme in [`registry/protocol.md`](../../registry/protocol.md).
- **The adapter interface** — any change to the six conformance capabilities or the SDK contract in [`sdk/`](../../sdk/).
- **The RFC process itself** — yes, RFCs about RFCs.

Do not open an RFC for:

- A new canonical loop (PR to [`loops/`](../../loops/) directly).
- A bug fix (open a bug report).
- A CLI feature that doesn't change the spec (open a feature request).
- A docs improvement (PR to [`docs/`](../../docs/) directly).

When in doubt, open a Discussion first. A maintainer will tell you whether
your idea needs an RFC.

---

## The RFC lifecycle

```
draft → review → accepted → implemented → stable
                 │
                 └→ rejected
```

1. **Draft.** You open an issue with the `[RFC]` prefix using the RFC issue
   template. A maintainer assigns an RFC number (`RFC-NNNN`). You PR a file
   at `spec/rfcs/RFC-NNNN-short-slug.md` with the full proposal.

2. **Review.** The RFC is discussed in GitHub Discussions for a minimum of
   two weeks. Maintainers and the community ask questions, raise concerns,
   and propose alternatives. You revise the RFC file in response.

3. **Accepted or rejected.** A maintainer closes the issue with a decision.
   Accepted RFCs are merged into `spec/rfcs/` and tracked in
   [`spec/loopfile-v1.md`](../loopfile-v1.md) under "Open questions" or the
   relevant section. Rejected RFCs are also merged, with a `Status: rejected`
   header and a one-paragraph rationale.

4. **Implemented.** An accepted RFC is implemented in a PR. The PR updates
   the spec, schema, grammar, and conformance suite. The RFC file is
   updated to `Status: implemented` with a link to the PR.

5. **Stable.** Once an RFC ships in a release, the RFC file is updated to
   `Status: stable` with the version number.

---

## RFC file format

```markdown
# RFC-NNNN: <title>

- Start date: YYYY-MM-DD
- Status: draft | review | accepted | rejected | implemented | stable
- Spec version: 1.0 | 1.1 | 2.0 | N/A
- PR: <link to PR that merged this RFC>
- Implementation: <link to PR that implemented this RFC, or "not yet">

## Summary

One paragraph.

## Motivation

Why is this change needed? What problem does it solve?

## Detailed design

The actual change. YAML, grammar, schema deltas, and worked examples.
Be concrete enough that an implementer doesn't have to make judgment calls.

## Alternatives considered

Including "do nothing" — why is the status quo not acceptable?

## Backwards compatibility

Does a 1.0 Loopfile still parse under this change? If not, what's the
migration path?

## Conformance impact

Which of the six conformance capabilities (Parse / Run / Verify / Inspect
/ Replay / Diff) does this affect? What must an adapter do to remain
conformant?

## Open questions

Things you don't know yet. List them explicitly so reviewers can help.

## Future possibilities

What might this enable later? Don't speculate too far — just sketch the
next obvious step.

## Acknowledgements

Anyone who contributed to the RFC.
```

---

## Numbering

RFC numbers are assigned sequentially starting from `RFC-0001`. Numbers are
never reused, even for rejected RFCs. Once an RFC number is assigned, it
belongs to that proposal forever.

---

## Review criteria

Maintainers evaluate RFCs on:

1. **Is the problem real?** Does it solve a pain that at least one real team
   has hit? (Adopter testimony helps.)
2. **Is the design minimal?** Does it solve the problem with the smallest
   possible spec delta? Features that "might be useful later" are rejected.
3. **Is it portable?** Does it work for any engine, or does it implicitly
   assume one runtime?
4. **Is it backwards-compatible?** If not, is the migration path clear?
5. **Is it conformance-testable?** Can we write a test that says "this
   adapter claims to support feature X; does it?"

An RFC that fails any of these is rejected. Rejection is not permanent —
the same idea can come back as a new RFC with new evidence.

---

## The current RFC list

| RFC | Title | Status |
| --- | --- | --- |
| [RFC-0001](RFC-0001-loopfile.md) | Loopfile v1.0 | implemented |
| [RFC-0002](RFC-0002-verification.md) | Verification Model | implemented |
| [RFC-0003](RFC-0003-replay.md) | Replay and Time-Travel | draft |
| [RFC-0004](RFC-0004-memory.md) | Loop Memory | draft |
| [RFC-0005](RFC-0005-registry.md) | Registry Protocol | draft |
| [RFC-0006](RFC-0006-marketplace.md) | Marketplace | draft |
| [RFC-0007](RFC-0007-adapter-interface.md) | Adapter Interface | draft |
| [RFC-0008](RFC-0008-observatory.md) | Loop Observatory | draft |
| [RFC-0009](RFC-0009-provenance.md) | Provenance and Signing | draft |
| [RFC-0010](RFC-0010-cost-accounting.md) | Cost Accounting | draft |

---

## License

All RFCs are licensed CC-BY-4.0, same as the rest of the spec.
