# Changelog

All notable changes to INFINI, the Loopfile spec, and the `infini` CLI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **INFINI × Hermes adapter** (`adapters/hermes/`) — governance brain: policy, memory, escalation, audit trails.
- **INFINI × OpenClaw adapter** (`adapters/openclaw/`) — execution runtime: browser, GitHub, terminal, filesystem tools.
- **Hybrid mode** — a Loopfile can declare `ENGINE.delegates.execution` to combine Hermes governance with OpenClaw execution.
- Three runnable demos:
  - `examples/hermes-governed-growth/` — claim-audit loop with policy, budget, escalation, audit.
  - `examples/openclaw-agent-loop/` — coding loop with file edits, tests, PR.
  - `examples/hybrid-hermes-openclaw/` — the killer demo: Hermes governs, OpenClaw executes, INFINI records.
- **Loop Observatory** section in README. Status: preview.
- Lineage statement in README: *Docker standardized containers. … INFINI standardizes autonomous work.*

### Changed
- **Rebrand: Loom → INFINI.** CLI command is now `infini`. Registry namespace is `infini/`.
- **Spec key: `LOOM:` → `LOOPFILE:`.** The top-level version key in every Loopfile is now `LOOPFILE: "1.0"`.
- **README logo** — replaced with the INFINI logo at `assets/logo.png`.
- **README killer section** — "INFINI for Hermes and OpenClaw" added near the top, above "Why INFINI exists".
- **Compatibility matrix** — Hermes and OpenClaw added as first-class rows.

### Removed
- **"Why this is viral"** section from README. Replaced with the calmer, factual "Why INFINI Wins" section.

---

## [1.0.0] — 2026-06-28

### Added
- Initial public release.
- Loopfile Specification v1.0 (`spec/loopfile-v1.md`), including:
  - `LOOPFILE`, `name`, `version`, `OBJECTIVE`, `AGENTS`, `STEPS`, `VERIFY`, `BUDGET`, `STOP_WHEN` fields.
  - Formal grammar (`spec/grammar.ebnf`).
  - JSON Schema (`spec/schema.json`).
  - Migration guide (`spec/migration.md`).
  - Engine compatibility matrix (`spec/compatibility.md`).
- `infini` CLI reference implementation:
  - `infini validate`, `infini inspect`, `infini replay`, `infini diff`, `infini ci` shipped.
  - `infini run`, `infini publish`, `infini install` require an engine adapter.
- The 12 canonical loops (Loopfile + essay + fixtures):
  `coding-loop`, `refactor-loop`, `test-gen-loop`, `debug-loop`, `review-loop`, `research-loop`, `content-loop`, `outreach-loop`, `migration-loop`, `doc-sync-loop`, `oncall-loop`, `sre-loop`.
- The **Loop Engineer Prompt** (`prompts/loop-engineer.md`).
- INFINI CI GitHub Action (`ci/`).
- MANIFESTO: *Loops > Chains*.

### Known limitations
- `infini run` requires an engine adapter. The INFINI Reference Engine ships first; Hermes and OpenClaw adapters ship in the same release.
- The Loop Observatory UI is in preview. The Inspector (`infini inspect`) ships; the full annotated timeline, cost waterfall, and replay studio are in active development.
- The public registry (`registry.infini.dev`) is coming soon. Local registry operations work today.

---

## Versioning

- **Spec versions** follow `MAJOR.MINOR` (`1.0`, `1.1`, `2.0`). Minor versions are additive; major versions may break conformance.
- **CLI versions** follow semver independently of the spec.
- **Registry versions** are immutable. Once `infini/coding-loop@1.2` is published, it cannot be republished.

See [`spec/migration.md`](spec/migration.md) for upgrade paths between spec versions.
