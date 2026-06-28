# INFINI Registry

> The public registry for Loopfiles. Versions are immutable and signed.

`infini publish` pushes a Loopfile to the registry. `infini install` pulls. Every version is content-addressed and signed; once a version is published, it cannot be republished or replaced.

---

## Status

- **Local registry operations** — shipped. You can `infini publish` to a local path and `infini install` from one.
- **Public registry at `https://registry.infini.dev`** — coming soon. The protocol below is final; the hosted endpoint is being stood up.

Until the public registry is live, use the local registry for testing:

```bash
infini publish ./Loopfile --registry ./local-registry/
infini install infini/coding-loop@1.0 --registry ./local-registry/
```

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

## Publishing

```bash
infini publish ./Loopfile
```

What this does:

1. Runs `infini validate` against [`spec/schema.json`](../spec/schema.json). Invalid Loopfiles are rejected.
2. Computes the content hash of the Loopfile.
3. Signs the hash with your configured signing key (Ed25519).
4. Uploads the Loopfile + signature + manifest to the registry.
5. Returns the immutable address: `infini/<name>@<version>`.

A published version is permanent. To fix a bug, publish a new version. To deprecate, mark the version deprecated (the registry keeps serving it but flags it).

---

## Installing

```bash
infini install infini/coding-loop@1.0
```

What this does:

1. Resolves `@1.0` to the latest `1.0.x` in the registry.
2. Downloads the Loopfile + signature.
3. Verifies the signature against the publisher's public key.
4. Writes the Loopfile to `./infini-cache/<ns>/<name>@<version>.yaml`.
5. Returns the local path.

You can then `infini run` the cached Loopfile or copy it into your repo.

---

## Searching

```bash
infini search "research loop with citations"
```

Returns matching Loopfiles with: name, version, description, publisher, star count (community), and last-updated timestamp.

---

## Signing

Every publisher generates an Ed25519 keypair:

```bash
infini keys generate
# writes ~/.infini/keys/ed25519.pub and ~/.infini/keys/ed25519.sec
```

The public key is registered with your namespace. The private key signs every published version. The registry refuses unsigned or wrongly-signed uploads.

If your private key is compromised, rotate it (`infini keys rotate`) and re-publish a new version under a new key. Old versions remain signed with the old key and are still verifiable.

---

## Mirroring

Anyone can mirror the registry. The registry is a content-addressed store; mirrors simply copy `(hash, signature, manifest)` triples. Mirrors are listed in `registry/mirrors.json` (to be added when the public registry ships).

---

## Protocol

The registry speaks HTTPS + JSON. The full protocol is documented in [`registry/protocol.md`](protocol.md) (planned). Endpoints:

| Method | Path | Description |
| --- | --- | --- |
| `GET`  | `/v1/resolve/<ns>/<name>@<version>` | Resolve a version to a content hash. |
| `GET`  | `/v1/fetch/<hash>` | Fetch a Loopfile by content hash. |
| `GET`  | `/v1/manifest/<ns>/<name>@<version>` | Fetch the signed manifest. |
| `POST` | `/v1/publish` | Publish a new version. Requires auth + signature. |
| `GET`  | `/v1/search?q=<query>` | Search Loopfiles. |

---

## Roadmap

- [ ] Public registry at `registry.infini.dev`
- [ ] Web UI for browsing
- [ ] Per-namespace signing key registration
- [ ] Mirror protocol spec
- [ ] Star / fork / PR-to-publish workflow

Until these ship, use the local registry for everything.

---

## License

MIT. See [repository LICENSE](../LICENSE).
