# RFC-0005: Registry Protocol

- Start date: 2026-06-28
- Status: draft
- Spec version: N/A (protocol, not Loopfile spec)
- PR: TBD
- Implementation: local registry ships in 1.0; public registry TBD

## Summary

Defines the protocol for the INFINI registry: a content-addressed store of
Loopfiles where every version is immutable, signed, and verifiable by
anyone.

## Motivation

Without a registry, Loopfiles are not shareable. Teams would copy-paste
YAML files between repos, lose track of versions, and have no way to
verify that a Loopfile came from who it claims to come from.

The registry must be:

- **Content-addressed.** A Loopfile is fetched by its hash, not its name.
  Names are aliases; hashes are truth.
- **Signed.** Every version is signed by the publisher. The registry
  verifies the signature on publish; clients verify it on install.
- **Immutable.** Once published, a version cannot be replaced. To fix a
  bug, publish a new version.
- **Mirrorable.** Anyone can mirror the registry. There is no single
  point of failure.
- **Open.** The protocol is documented; anyone can implement a server or
  a client.

## Detailed design

### Addressing

```
infini/coding-loop@1.2.0
└──┬─┘ └────┬────┘ └─┬─┘
  ns        name    version
```

- `ns` is the publisher's namespace (GitHub user/org, or `infini` for
  canonical loops).
- `name` is the Loopfile's `name` field (a slug).
- `version` is a semver version. `@1.2` resolves to the latest `1.2.x`;
  `@1.2.0` is exact.

### Content addressing

Every published version has:

1. A **content hash** — `sha256` of the canonicalized Loopfile.
2. A **signature** — Ed25519 signature of the content hash by the
   publisher's key.
3. A **manifest** — JSON with: ns, name, version, content_hash, signature,
   publisher_public_key, published_at.

The manifest is what `infini install` fetches first. The content hash is
then used to fetch the Loopfile itself. The signature is verified against
the publisher's registered public key.

### Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET`  | `/v1/resolve/<ns>/<name>@<version>` | Resolve to a manifest. |
| `GET`  | `/v1/fetch/<hash>` | Fetch a Loopfile by content hash. |
| `GET`  | `/v1/manifest/<ns>/<name>@<version>` | Fetch a manifest directly. |
| `POST` | `/v1/publish` | Publish a new version. Requires auth + signature. |
| `GET`  | `/v1/search?q=<query>` | Search Loopfiles. |
| `GET`  | `/v1/keys/<ns>` | Fetch a namespace's registered public keys. |
| `POST` | `/v1/keys/<ns>/rotate` | Rotate a namespace's signing key. |

The full protocol is in [`registry/protocol.md`](../../registry/protocol.md).

### Mirroring

A mirror is a read-only replica that serves `/v1/fetch/<hash>` and
`/v1/manifest/<ns>/<name>@<version>` from a local cache. Mirrors sync by
polling `/v1/resolve` for namespaces they care about and fetching any new
content hashes. Mirrors are listed in `registry/mirrors.json`.

### Key rotation

If a publisher's private key is compromised:

1. `POST /v1/keys/<ns>/rotate` with the old key, signing the new public key.
2. The registry marks the old key as revoked but continues to serve
   existing versions (they're still signed with the old key, and the old
   key's revocation is recorded).
3. New publishes must use the new key.

Old versions remain verifiable because the registry keeps a record of all
keys ever registered to a namespace.

## Alternatives considered

- **Git as the registry.** Rejected — Git doesn't support content
  addressing of individual files cleanly, and signatures are per-commit,
  not per-version.
- **OCI artifacts (Docker registry).** Considered. Rejected for v1 because
  the Loopfile is a single YAML file, not a layered artifact. Could be
  revisited if Loopfiles grow to include bundled fixtures.
- **Centralized, no mirroring.** Rejected — single point of failure.
- **No signing.** Rejected — without signing, anyone could publish under
  any namespace.

## Backwards compatibility

v1.0. No prior version.

## Conformance impact

The registry is not part of the Loopfile spec; it's a separate protocol.
However, `infini install` and `infini publish` depend on it, and the
`Install` and `Publish` CLI commands are gated on a registry (local or
remote).

## Open questions

- Should the registry support Loopfile bundles (Loopfile + fixtures + essay
  as a single publishable unit)? Current answer: no, keep it simple.
  Revisit at v1.1.
- Should there be a "verified publisher" badge for namespaces that have
  undergone some review? Current answer: no, the registry is neutral. The
  compatibility matrix and adopters page serve this role.
- How are namespace squats handled? Current answer: GitHub-authenticated
  namespaces; first-come on non-GitHub namespaces. Open for debate.

## Future possibilities

- v1.1: bundle publishing (Loopfile + fixtures).
- v1.2: namespace transfers (publisher A hands namespace to publisher B).
- v2.0: marketplace UI on top of the registry (see
  [RFC-0006](RFC-0006-marketplace.md)).

## Acknowledgements

The protocol is modeled on PyPI (namespacing), npm (semver resolution),
Cargo (content addressing), and TUF (signing and key rotation).
