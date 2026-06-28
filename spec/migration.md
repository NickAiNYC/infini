# Loopfile Migration Guide

How to move a Loopfile from one spec version to the next.

> **INFINI runs Loopfiles.** This document is the upgrade path between spec versions.

---

## Current version

| Spec version | Status  | Released     | Superseded by |
| ------------ | ------- | ------------ | ------------- |
| `1.0`        | Draft   | 2026-06-28   | —             |

---

## Migration: pre-1.0 → 1.0

Before `1.0`, the project was branded `Loom` and the top-level version key was `LOOM`. The 1.0 release renamed the spec artifact to `Loopfile` and the engine to `INFINI`.

### Rename the version key

```diff
- LOOM: "1.0"
+ LOOPFILE: "1.0"
```

### Rename CLI invocations

```diff
- loom run ./Loopfile
+ infini run ./Loopfile

- loom inspect runs/latest/
+ infini inspect runs/latest/

- loom install loom/coding-loop@1.0
+ infini install infini/coding-loop@1.0
```

### Rename registry references

```diff
- loom install loom/coding-loop@1.0
+ infini install infini/coding-loop@1.0
```

Registry entries published under the `loom` namespace will be mirrored to `infini` during the migration window. Both namespaces resolve until 2026-09-30, after which only `infini` remains.

### Rename CI

```diff
- uses: loom/ci@v1
+ uses: infini/ci@v1
```

The `loom/ci` action will continue to forward to `infini/ci` until the deprecation window closes.

### Automated migration

```bash
infini migrate ./Loopfile        # in-place rewrite
infini migrate ./Loopfile --diff # show what would change
```

The migrator is conservative: it refuses to rewrite a Loopfile that contains keys it does not recognize. For those, file an issue with `infini --debug migrate` output attached.

---

## Migration: 1.0 → 1.1 (planned)

The 1.1 release is additive. No breaking changes. Planned additions:

- `PACKS:` — declare a bundle of loops with shared inputs.
- `METRICS:` — declare additional metrics to expose in the trace.
- `HOOKS:` — declare lifecycle hooks (`pre_step`, `post_verify`, `on_failure`).

A 1.0 Loopfile is automatically a valid 1.1 Loopfile.

---

## Migration: 1.x → 2.0 (not yet planned)

The 2.0 release will introduce breaking changes. Likely candidates:

- Typed `OBJECTIVE` (structured objective instead of freeform string).
- First-class composition (`CALLS:` instead of `depends_on` for sub-loops).
- Built-in `METRICS:` block promoted from 1.1.

A 2.0 migrator will ship alongside the spec. Loopfiles that cannot be auto-migrated will be flagged with a human-readable migration report.

---

## Backward compatibility

The INFINI Reference Engine supports the two most recent minor versions of the current major. Engines are encouraged but not required to follow the same policy.

| Engine version | Supports Loopfile spec |
| -------------- | ---------------------- |
| `infini 1.0.x` | `1.0`                  |
| `infini 1.1.x` | `1.0`, `1.1`           |
| `infini 2.0.x` | `1.1`, `2.0`           |

---

## Filing migration issues

If `infini migrate` fails on your Loopfile:

1. Run `infini --debug migrate ./Loopfile > migrate.log`.
2. Open an issue at `https://github.com/NickAiNYC/infini/issues`.
3. Attach `migrate.log` and the Loopfile (with secrets redacted).

We treat migration failures as P0 bugs.
