# RFC-0009: Provenance and Signing

- Start date: 2026-06-28
- Status: draft
- Spec version: N/A (cross-cutting)
- PR: TBD
- Implementation: registry signing in 1.0; full provenance in 1.1

## Summary

Defines how INFINI establishes trust: who wrote this Loopfile, who ran it,
what they ran it on, what artifacts it produced, and how we know none of
that was tampered with after the fact.

## Motivation

Agent systems produce work that affects the real world (code, emails,
decisions, audit records). When an agent ships something, the question is
always: *who is responsible?*

Provenance must be:

- **End-to-end.** From Loopfile authorship to artifact production, every
  step is attributable.
- **Verifiable.** Trust is established by signatures, not by claims.
- **Tamper-evident.** You can't edit a trace without breaking a hash
  chain.
- **Portable.** Provenance travels with the trace, not with the engine.

## Detailed design

### Layer 1: Loopfile signing

Every Loopfile published to the registry is signed by its publisher
(RFC-0005). The signature is Ed25519 over the content hash. The publisher's
public key is registered with their namespace.

`infini install` verifies the signature before caching. Unsigned
Loopfiles can be installed only with `--allow-unsigned`.

### Layer 2: Run signing

Every `run.json` trace is signed by the engine that produced it. The
engine has its own keypair, separate from any publisher keypair. The
signature covers:

- The Loopfile hash (so you know what was run).
- The engine identity and version.
- The start and end timestamps.
- The outcome.
- The artifact hashes.

```json
{
  "provenance": {
    "loopfile_hash": "sha256:9f3a...",
    "loopfile_signature": "ed25519:7c1a... (verified against infini namespace)",
    "engine": { "type": "hermes", "version": "1.4.0" },
    "engine_signature": "ed25519:2b4f... (verified against hermes adapter key)",
    "started_at": "2026-06-28T10:42:50Z",
    "ended_at":   "2026-06-28T10:47:22Z",
    "outcome": "verified",
    "artifact_hashes": {
      "decision.signed.md": "sha256:1c8b...",
      "audit/log.jsonl":    "sha256:3f7d..."
    }
  }
}
```

### Layer 3: Artifact signing

Individual artifacts can be signed by the engine or by a dedicated
signing agent. This is most important for governance artifacts (audit
logs, postmortems) where the signature is the legal record.

The Hermes adapter signs every `audit/log.jsonl` it produces. The
signature is in the trace's `provenance.artifact_signatures` field.

### Layer 4: Trace chain

For loops with multiple iterations, each iteration's trace is chained to
the previous iteration's hash:

```json
{
  "iteration": 3,
  "previous_iteration_hash": "sha256:abc1...",
  "this_iteration_hash":     "sha256:def2..."
}
```

This makes the trace tamper-evident: editing any step breaks the hash
chain from that point forward.

### Layer 5: Cross-engine verification

A trace produced by engine A can be verified by engine B (or by the CLI
itself) using engine A's public key. This is what makes provenance
portable: you don't have to trust the engine that produced a trace, you
just have to verify its signature.

## Alternatives considered

- **No signing; trust the engine.** Rejected — engines can be compromised
  or buggy. Signatures make trust verifiable.
- **Single signing key per engine.** Rejected — key rotation must be
  possible. RFC-0005 covers this.
- **Blockchain-based provenance.** Rejected — overkill. Ed25519 and a
  hash chain are sufficient.
- **Signed artifacts only (no trace signing).** Rejected — the trace is
  the primary record. Artifacts are secondaries.

## Backwards compatibility

v1.0. Loopfile signing is part of v1.0 (registry). Run signing is part of
v1.0 (engines that emit `run.json` must sign it). Artifact signing is
optional in v1.0, required for governance adapters (Hermes) in v1.0.

## Conformance impact

Engines that implement `Inspect Trace` must sign their traces. Engines
that don't sign are not conformant, even if their `run.json` is otherwise
valid.

## Open questions

- How are engine public keys distributed? Current answer: registered with
  the adapter's namespace in the registry. Open for debate.
- What happens if an engine's key is compromised? Current answer: key
  rotation per RFC-0005. Old traces remain verifiable against the old
  key, with a revocation record.
- Should provenance include the model used (not just `model_tier`)?
  Current answer: no, models are not stable identifiers. The engine
  identity is the unit of trust.

## Future possibilities

- v1.1: full provenance graph — visualize the chain from Loopfile author
  to artifact in the Observatory.
- v1.2: third-party attestation — independent auditors can sign traces
  they've reviewed.
- v2.0: provenance standardization — align with SLSA / in-toto for
  supply-chain integrity.

## Acknowledgements

The provenance model is borrowed from SLSA (Supply-chain Levels for
Software Artifacts), in-toto, TUF (The Update Framework), and Git's
commit signing.
