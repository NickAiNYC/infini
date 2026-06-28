# Registry Protocol

> *Planned. The protocol below is final; the hosted endpoint is being stood up.*

The INFINI registry is a content-addressed store of Loopfiles. Every version is immutable, signed, and verifiable by anyone.

---

## Addressing

A Loopfile is addressed by namespace, name, and version:

```
infini/coding-loop@1.0
└──┬─┘ └────┬────┘ └┘
  ns        name   version
```

- `ns` is the publisher's namespace (a GitHub user/org, or `infini` for canonical loops).
- `name` is the Loopfile's `name` field (a slug).
- `version` is a semver version. `@1.0` resolves to the latest `1.0.x`. `@1.0.2` is exact.

---

## Content addressing

Every published version has:

1. A **content hash** — `sha256` of the canonicalized Loopfile.
2. A **signature** — Ed25519 signature of the content hash by the publisher's key.
3. A **manifest** — JSON document with: ns, name, version, content_hash, signature, publisher_public_key, published_at.

The manifest is what `infini install` fetches first. The content hash is then used to fetch the Loopfile itself. The signature is verified against the publisher's registered public key.

---

## Endpoints

The registry speaks HTTPS + JSON. All endpoints are versioned under `/v1`.

| Method | Path | Description |
| --- | --- | --- |
| `GET`  | `/v1/resolve/<ns>/<name>@<version>` | Resolve a version to a content hash. Returns the manifest. |
| `GET`  | `/v1/fetch/<hash>` | Fetch a Loopfile by content hash. Returns the raw YAML. |
| `GET`  | `/v1/manifest/<ns>/<name>@<version>` | Fetch the signed manifest. |
| `POST` | `/v1/publish` | Publish a new version. Requires auth + signature. |
| `GET`  | `/v1/search?q=<query>` | Search Loopfiles. Returns matching manifests. |
| `GET`  | `/v1/keys/<ns>` | Fetch a namespace's registered public keys. |
| `POST` | `/v1/keys/<ns>/rotate` | Rotate a namespace's signing key. Requires auth with the old key. |

---

## Publishing

```http
POST /v1/publish
Authorization: Bearer <publisher_token>
Content-Type: application/json

{
  "ns": "infini",
  "name": "coding-loop",
  "version": "1.2.0",
  "loopfile": "<base64-encoded Loopfile YAML>",
  "content_hash": "sha256:9f3a...",
  "signature": "ed25519:7c1a...",
  "publisher_public_key": "ed25519:2b4f..."
}
```

The registry:

1. Verifies the content hash matches the Loopfile.
2. Verifies the signature against the publisher's registered public key.
3. Checks that `(ns, name, version)` does not already exist. Versions are immutable.
4. Stores the manifest and Loopfile.
5. Returns the immutable address: `infini/coding-loop@1.2.0`.

---

## Installing

```http
GET /v1/resolve/infini/coding-loop@1.2
```

Returns:

```json
{
  "ns": "infini",
  "name": "coding-loop",
  "version": "1.2.0",
  "content_hash": "sha256:9f3a...",
  "signature": "ed25519:7c1a...",
  "publisher_public_key": "ed25519:2b4f...",
  "published_at": "2026-07-15T10:42:50Z"
}
```

The client then:

1. Fetches the Loopfile by content hash: `GET /v1/fetch/sha256:9f3a...`
2. Verifies the content hash matches.
3. Verifies the signature against the publisher's public key.
4. Caches locally.

---

## Mirroring

Anyone can mirror the registry. A mirror is a read-only replica that serves `/v1/fetch/<hash>` and `/v1/manifest/<ns>/<name>@<version>` from a local cache.

Mirrors sync by polling `/v1/resolve` for namespaces they care about and fetching any new content hashes. Mirrors are listed in `registry/mirrors.json` (to be added when the public registry ships).

---

## Key rotation

If a publisher's private key is compromised:

1. `POST /v1/keys/<ns>/rotate` with the old key, signing the new public key.
2. The registry marks the old key as revoked but continues to serve existing versions (they're still signed with the old key, and the old key's revocation is recorded).
3. New publishes must use the new key.

Old versions remain verifiable because the registry keeps a record of all keys ever registered to a namespace.

---

## Status

- Local registry operations: shipped.
- Public registry at `registry.infini.dev`: coming soon.
- This protocol: final, open for feedback.

Until the public registry ships, use the local registry:

```bash
infini publish ./Loopfile --registry ./local-registry/
infini install infini/coding-loop@1.0 --registry ./local-registry/
```
