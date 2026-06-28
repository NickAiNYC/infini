# Migration Notes — v0.1.0 → v0.2.0

**No breaking changes.** v0.1.0 Loopfiles run unchanged on v0.2.0.

---

## What changed

### Added (non-breaking)

- `TOOLS` block in the schema (MCP support) — optional, ignored by v0.1.0 engines
- `infini certify` command — new, doesn't affect existing commands
- `infini conformance` command — new, doesn't affect existing commands
- `sdk/`, `brand/`, `registry/official/`, `marketplace/` — new directories
- `tests/corpus/` — 10 new canonical benchmark cases
- 17-chapter handbook with cross-links

### Changed (non-breaking)

- CI workflow now installs from source (`pip install -e './cli[dev]'`) instead of PyPI
- `spec/compatibility.md` is now auto-generated from adapter manifests + certification reports
- Mock verifier has a `deterministic` parameter (default `False` for backward compat)

### Deprecated

Nothing.

### Removed

Nothing.

---

## What you need to do

### If you're a Loopfile author

Nothing. Your v0.1.0 Loopfiles work unchanged.

### If you're an adapter author

Nothing required. Optionally:

1. Run `infini certify adapters/<your-adapter> --mock` to generate a certification report
2. Add your adapter to `registry/community/` following the [publishing guide](../sdk/publishing-guide.md)

### If you're a CLI user

Nothing. The new commands (`certify`, `conformance`) are additive.

---

## Schema version

The spec version remains `LOOPFILE: "1.0"`. No migration needed.

See [spec versioning](../spec/versions.md) for the full versioning policy.
