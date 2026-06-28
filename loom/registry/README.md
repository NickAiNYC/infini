# Loom Registry — RFC

> Status: draft. Not live. We are designing in the open.

The registry is the npm-for-loops layer of Loom. It is the thing that turns Loopfiles from one-off scripts into versioned, signed, installable packages.

---

## Why a registry

A spec without a registry is just a document. A registry without a spec is just a database. Together they create network effects: every published loop makes every other loop more valuable, because every published loop is a reusable starting point.

The Docker parallel is exact: Dockerfile + Docker Hub. Loom has the Loopfile; the registry is Hub.

---

## Operations

```bash
loom install loom/coding-loop@1.2      # pull a loop
loom publish ./Loopfile                # push a loop
loom search "research with citations"  # search
loom info   loom/coding-loop           # metadata, versions, downloads
loom unpublish loom/coding-loop@1.0    # remove (only unlisted versions, never latest)
```

---

## Loop reference

```
<owner>/<name>@<semver>
```

- `owner`: a user or org (e.g. `loom`, `acme`, `jane`)
- `name`: lowercase-kebab, matches `name:` in Loopfile
- `semver`: standard semver, immutable once published

---

## Trust

- Every published version is **content-addressed** (SHA-256 of the Loopfile body)
- Every published version is **signed** by the publisher's key (Sigstore)
- Every published version is **immutable** — you can unpublish a version only if it has zero installs and is < 30 days old

---

## Discovery

- `loom search` ranks by: relevance, downloads, stars, verification tier count
- Loops with <2 verification tiers are marked `UNVERIFIED` and down-ranked
- Loops with no README are down-ranked
- Loops with no fixtures cannot be in the "official" namespace

---

## Namespaces

- `loom/*` — official, curated, requires RFC + review
- `<org>/*` — org-owned, requires org verification
- `<user>/*` — personal, open to anyone

---

## Storage (planned)

- Backend: S3-compatible object store for Loopfile bodies
- Index: Postgres for metadata, search, install counts
- CDN: edge-cached for fast `loom install`

---

## Trust signals shown to users

```
loom/coding-loop  v1.2.0  ★ 2.1k  ↓ 18k  ✓ verified (3 tiers)  signed
```

| signal | meaning |
|--------|---------|
| ★ | stars (GitHub-style) |
| ↓ | install count |
| ✓ verified | has ≥2 verification tiers and they pass on the published fixtures |
| signed | publisher signature valid |

---

## Open questions

- Should the registry run loops against fixtures on publish (gate)? Or only on `loom ci` (signal)?
- Should we support paid loops? (Probably no for v1.)
- Should we support loop dependencies (`FROM: loom/other-loop`) with automatic resolution?

These are deferred. Ship v1, learn, iterate.

---

## Timeline

- **Q1**: spec final, CLI ships `validate`, `inspect`, `replay`, `diff`, `ci`
- **Q2**: registry alpha — read-only mirror of GitHub repos under `loom/*`
- **Q3**: registry beta — `publish` and `install` live, signing required
- **Q4**: registry GA — full search, namespaces, trust signals

---

We are building this in the open. If you want to help, open an RFC in `spec/rfcs/`.
