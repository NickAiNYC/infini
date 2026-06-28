# Changelog

All notable changes to Loom will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Registry RFC (`registry/README.md`)
- Inspector, replay, diff, ci commands in `cli/loom.py`

## [0.1.0] — 2026-06-28

### Added
- **Loopfile spec v1.0** (`spec/loopfile-v1.md`)
- **Trace format v1** (`spec/trace-format-v1.md`)
- **State format v1** (`spec/state-format-v1.md`)
- **12 canonical loops** in `loops/`:
  - `coding-loop`, `refactor-loop`, `test-gen-loop`, `debug-loop`
  - `review-loop`, `research-loop`, `content-loop`, `outreach-loop`
  - `migration-loop`, `doc-sync-loop`, `oncall-loop`, `sre-loop`
- **Loop Engineer operating prompt** (`prompts/loop-engineer.md`)
- **Manifesto** (`MANIFESTO.md`) — *Loops > Chains*
- **CLI reference implementation** (`cli/loom.py`) with:
  - `run`, `validate`, `inspect`, `replay`, `diff`
  - `ci` (fixtures mode), `engines`, `search`, `install`, `publish`
- **GitHub Action** (`.github/workflows/loop-ci.yml`) for `loom ci` on PRs
- **README** with the 30-second pitch and quickstart

### Known limitations
- `loom run` requires an engine adapter (not bundled in v0.1)
- `loom install` and `loom publish` require the registry (RFC stage)
- `loom inspect` and `loom replay` are CLI-only; web UI planned for v0.3
