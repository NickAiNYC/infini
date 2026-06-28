# Changelog

All notable changes to INFINI, the Loopfile spec, and the `infini` CLI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — protocol-grade expansion

#### RFC system
- **`spec/rfcs/README.md`** — RFC process (modeled on Rust, Kubernetes KEPs, Python PEPs).
- **10 RFCs:** RFC-0001 Loopfile, RFC-0002 Verification, RFC-0003 Replay, RFC-0004 Memory, RFC-0005 Registry, RFC-0006 Marketplace, RFC-0007 Adapter Interface, RFC-0008 Observatory, RFC-0009 Provenance, RFC-0010 Cost Accounting.

#### Adapter SDK
- **`sdk/README.md`** — Adapter SDK overview: 6 capabilities, install, anatomy.
- **`sdk/adapter-interface.md`** — Normative interface reference: types, base class, capability contracts, hybrid mode, conformance testing.
- **`sdk/examples/minimal-adapter.md`** — Smallest possible adapter (PARSE only).

#### Handbook (10 chapters)
- **`docs/handbook/`** — Why Loopfiles · Design Philosophy · Loop Engineering · Verification · Memory · Observability · Replay · Governance · Portability · Standards.

#### Design Patterns (13 patterns)
- **`docs/patterns/`** — Retry · Human Approval · Budget Guard · Parallel Workers · Fan Out · Fan In · Verification Gate · Reflection Loop · Research Loop · Planning Loop · Memory Update · Escalation · Self Improvement.

#### Anti-Patterns (9 anti-patterns)
- **`docs/anti-patterns/`** — Infinite Loops · Hallucination Chains · Missing Verification · Unbounded Costs · Hidden State · Tool Spam · Prompt Soup · Over-Planning · No Exit Condition.

#### Canonical loop expansion (12 loops × 5 new files each)
- Every canonical loop now ships with: `Loopfile.yaml`, `README.md`, `essay.md`, `diagram.svg`, `trace.json`, `verification.md`, `benchmark.md`, `replay.md`.

#### Marketplace (preview)
- **`marketplace/`** — 12 category pages (Research, Coding, Compliance, Security, Sales, SEO, Marketing, Healthcare, Finance, Legal, Education, Infrastructure). Clearly labeled Preview.

#### Benchmark suite
- **`benchmarks/`** — 5 benchmark specs: coding-loop, research-loop, compliance-loop, browser-loop, hybrid-loop. Methodology + reporting standards.

#### Registry metadata
- **`registry/metadata-schema.md`** — Loop Quality Score (8 sub-scores, weighted to 100) + registry metadata fields schema.

#### Loop Observatory expansion
- **`assets/observatory.png`** — swimlane trace (existing).
- **`assets/loop-graph.png`** — decision graph view (new).
- **`assets/verification-dashboard.png`** — verification dashboard view (new).
- **`assets/replay-timeline.png`** — replay timeline view (new).
- **`assets/marketplace.png`** — marketplace mockup (new).

#### GitHub Excellence
- **`.github/ISSUE_TEMPLATE/`** — bug report, feature request, RFC proposal, config.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — PR template with spec-impact checklist.
- **`SECURITY.md`** — supported versions, disclosure process, scope, signing.
- **`CODE_OF_CONDUCT.md`** — Contributor Covenant 2.1.
- **`.github/FUNDING.yml`** — funding policy (not currently accepting sponsorship).
- **`ROADMAP.md`** — themed roadmap: Spec, Reference Engine, Adapters, Registry, Discipline, Community.

### Added — initial INFINI drop
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
- **README restructured** — Docker-style ordering: Vision · Demo · Architecture · Observatory · Hermes · OpenClaw · Loopfile · Examples · Marketplace · Registry · Specification · Adapters · Roadmap · Contributing · License · Community.
- **Compatibility matrix** — Hermes and OpenClaw added as first-class rows.

### Removed
- **"Why this is viral"** section from README. Replaced with the calmer, factual lineage statement.

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
