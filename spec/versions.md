# Spec Versioning

How the Loopfile spec is versioned, what stability guarantees exist, and
how migrations will work as the spec evolves.

> **Current spec version:** `LOOPFILE: "1.0"`
> See [`loopfile-v1.md`](loopfile-v1.md) for the normative spec.

---

## Versioning scheme

The Loopfile spec follows a `MAJOR.MINOR` version scheme:

- **MAJOR** (`1.0`, `2.0`): Breaking changes. A Loopfile written for
  `1.0` may not parse or run correctly under `2.0` without migration.
- **MINOR** (`1.0`, `1.1`, `1.2`): Additive changes. A Loopfile written
  for `1.0` is always valid under `1.1` and `1.2`. New fields are
  optional; existing fields keep their semantics.

Patch fixes (typos, clarifications, schema bug fixes) do not bump the
spec version. They are noted in [`CHANGELOG.md`](../CHANGELOG.md).

---

## What is stable in v1.0

The following are **stable** and will not change without a major version
bump:

| Feature | Guarantee |
| --- | --- |
| `LOOPFILE: "1.0"` version key | Required in every Loopfile. Value is exactly `"1.0"`. |
| `name`, `version`, `OBJECTIVE` | Required top-level fields. Semantics fixed. |
| `AGENTS` | List of agent definitions with `name`, `role`, `model_tier`, `tools`. |
| `STEPS` | List of step definitions with `id`, `name`, `action`, `uses`, `produces`, `depends_on`. |
| `VERIFY` | Block with `syntactic`, `semantic`, `confidence_threshold`. |
| `BUDGET` | Block with `dollars`, `minutes`, optional `tokens`. |
| `STOP_WHEN` | List of stop predicates. |
| Trace format (`run.json`) | Top-level fields: `loopfile`, `engine`, `started_at`, `ended_at`, `iterations`, `steps`, `verifications`, `budget`, `outcome`. |

A Loopfile that uses only these fields is portable across every v1.x
engine. This is the contract.

---

## What is experimental in v1.0

The following are **experimental** and may change semantics in a minor
version bump (but not without a migration note):

| Feature | Status | Notes |
| --- | --- | --- |
| `TOOLS` (MCP) | experimental | The `TOOLS` block is in the schema and spec, but the reference engine does not yet load real MCP servers. Semantics may adjust as implementation proceeds. See [`docs/mcp-strategy.md`](../docs/mcp-strategy.md). |
| `LESSONS` | experimental | The `LESSONS` block is in the schema, but memory persistence is not yet implemented in the reference engine. |
| `STATE` | experimental | The `STATE` block is in the schema, but resume-from-state is not yet implemented. |
| `ENGINE.delegates` | experimental | Hybrid mode (Hermes delegates to OpenClaw) is specified but not yet implemented in the reference engine. |
| `retry` on steps | experimental | The `retry` field is in the schema, but the reference engine's retry behavior is basic. |

Experimental features are declared in the spec so adopters can see
what's coming, but they should not be relied upon in production until
they move to "stable."

---

## Compatibility policy

### Patch (no version bump)

- Documentation fixes
- Example fixes
- Schema bug fixes (e.g., a field that was supposed to be optional but
  was accidentally required)
- Conformance test fixes

A patch release does not change the spec version string. A Loopfile
valid before the patch is valid after.

### Minor (`1.0` → `1.1`)

- New optional fields (e.g., `PACKS:`, `METRICS:`, `HOOKS:`)
- New optional capabilities (e.g., a new `STOP_WHEN` predicate)
- New experimental features moved to stable
- Clarifications that don't change semantics

A minor release is **backward-compatible**. A Loopfile written for `1.0`
is valid under `1.1`. A Loopfile using `1.1` features may not run on a
`1.0` engine, but it will still parse (the `1.0` engine ignores unknown
fields).

### Major (`1.x` → `2.0`)

- Removing a field
- Changing a field's semantics
- Changing the trace format in a breaking way
- Changing the `LOOPFILE` version key (e.g., `"1.0"` → `"2.0"`)

A major release requires a migration guide ([`migration.md`](migration.md)).
Loopfiles written for the previous major version must be migrated. The
`infini migrate` command (planned) will automate this where possible.

**What cannot break without v2:**

- The six top-level required fields: `LOOPFILE`, `name`, `version`,
  `OBJECTIVE`, `AGENTS`, `STEPS`, `VERIFY`, `BUDGET`, `STOP_WHEN`.
- The `run.json` trace format's top-level fields.
- The conformance capability names: `parse_loopfile`, `run_loop`,
  `verify`, `inspect_trace`, `replay`, `diff`.

These are the load-bearing parts of the spec. They are the contract
that makes Loopfiles portable. Breaking them requires a major version
bump and a migration guide.

---

## Migration path

When v2.0 ships:

1. `infini migrate ./Loopfile` rewrites a `1.x` Loopfile to `2.0`.
2. The migration guide ([`migration.md`](migration.md)) documents every
   change and its rationale.
3. Engines should support both `1.x` and `2.0` for at least one major
   release cycle after `2.0` ships.
4. The registry accepts both versions; `infini install` resolves to the
   latest compatible version.

Until v2.0 ships, no migration is needed. v1.x Loopfiles are forward-
compatible.

---

## Engine conformance

Engines declare which spec version they support in their `adapter.yaml`:

```yaml
adapter:
  name: hermes
  version: 1.0.0
  spec: LOOPFILE-1.0
```

The `spec` field must match the `LOOPFILE` version in the Loopfile. An
engine that declares `LOOPFILE-1.0` must support all stable v1.0
features. Support for experimental features is optional and tracked in
the [compatibility matrix](compatibility.md).

---

## See also

- [`loopfile-v1.md`](loopfile-v1.md) — the normative spec
- [`schema.json`](schema.json) — the JSON Schema
- [`compatibility.md`](compatibility.md) — engine support matrix
- [`migration.md`](migration.md) — version-to-version migration (currently empty until v2.0)
- [`../CHANGELOG.md`](../CHANGELOG.md) — change history
