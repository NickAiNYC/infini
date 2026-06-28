# RFC-0006: Marketplace

- Start date: 2026-06-28
- Status: draft
- Spec version: N/A (UI on top of registry)
- PR: TBD
- Implementation: mock at [`marketplace/`](../../marketplace/); real impl post-registry launch

## Summary

Defines the marketplace: a browseable view of the registry, organized by
category, with featured loops, contributor profiles, and verification
badges. The marketplace is a UI on top of the registry protocol defined in
[RFC-0005](RFC-0005-registry.md); it adds no new protocol.

## Motivation

A registry is searchable but not browsable. New users don't know what to
search for; they want to see "what's good for research?" or "what's good
for compliance?" The marketplace is the front door.

The marketplace must be:

- **Honest.** No fake featured loops, no fake stars, no fake downloads.
  Until real adoption exists, the marketplace shows real zeros.
- **Categorized.** Loops are organized by use case (research, coding,
  compliance, etc.), not by adapter.
- **Verification-forward.** A loop's verification score is its most
  important feature. Loops without verification are not featured.
- **Mock-first.** The current marketplace is a static mock, clearly labeled
  Preview. The real marketplace ships after the registry.

## Detailed design

### Categories

```text
Research         Coding          Compliance     Security
Sales            SEO             Marketing      Healthcare
Finance          Legal           Education      Infrastructure
```

Each category has:

- A `README.md` with the category definition and inclusion criteria.
- A `featured.md` listing 0–3 featured loops (curated, not algorithmic).
- A `new.md` listing the most recently published loops in the category.
- A `contributors.md` listing the most active contributors in the category.

Until the registry is live, all of these files contain "No loops
published yet."

### Verification badge

Every loop in the marketplace shows a verification badge:

- ✅ Verified — the loop's `VERIFY` block passes against its fixtures, and
  the trace is reproducible.
- ⚠ Unverified — the loop has a `VERIFY` block but it doesn't pass.
- ❌ No verification — the loop has no `VERIFY` block. These are not
  featured.

The badge is computed by `infini ci` against the loop's published fixtures.
It is not a publisher claim; it is a registry-computed fact.

### Supported engines

Every loop shows which engines it has been tested against:

```text
Supported engines: INFINI Reference ✅ · Hermes ✅ · OpenClaw 🚧
```

This is pulled from the compatibility matrix in
[`spec/compatibility.md`](../compatibility.md), not from the loop itself.

### Marketplace metadata

Each loop in the marketplace exposes:

- Name and version
- Publisher (namespace)
- Description
- Category
- Tags
- Verification badge
- Supported engines
- Estimated runtime
- Estimated cost
- Required tools
- Maintainer
- License
- Downloads (real, not faked)
- Compatibility (which engines, which spec versions)

The metadata schema is in [`registry/metadata-schema.md`](../../registry/metadata-schema.md).

## Alternatives considered

- **Algorithmic featured loops.** Rejected — algorithms can be gamed.
  Featured loops are curated by maintainers, with clear criteria.
- **Star ratings.** Rejected — stars measure popularity, not quality. The
  verification badge measures quality. We surface the latter.
- **Comments and reviews.** Rejected for v1 — too much moderation burden.
  Discussions happen in GitHub Discussions.
- **Paid placement.** Rejected permanently. The marketplace is neutral.

## Backwards compatibility

N/A — the marketplace is additive.

## Conformance impact

None. The marketplace is a UI on top of the registry.

## Open questions

- Who curates featured loops? Current answer: maintainers, with a public
  nomination process in GitHub Discussions.
- How are categories added or removed? Current answer: RFC, same as spec
  changes.
- What happens when a loop's verification starts failing (e.g., a model
  change breaks a semantic check)? Current answer: the badge flips to
  ⚠ and the publisher is notified.

## Future possibilities

- v1.1: real marketplace UI at `marketplace.infini.dev`.
- v1.2: contributor profiles with publish history and verification rates.
- v2.0: loop packs — bundles of related loops sold (free or paid) as a
  unit. Paid packs would require a payment integration, which is
  intentionally out of scope for now.

## Acknowledgements

The marketplace model is borrowed from VS Code Marketplace (categories,
featured), Docker Hub (verification, official images), and Crates.io
(download counts, version history).
