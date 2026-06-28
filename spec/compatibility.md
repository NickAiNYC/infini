# Engine Compatibility Matrix

> Auto-generated from `adapters/*/adapter.yaml` and `registry/certifications/*.json`.
> Run `python ci/generate_matrix.py` to regenerate.

## Conformance levels

An adapter is **certified** when it passes all required conformance cases.
See [`RELEASE.md`](../RELEASE.md) for the certification process.

Legend: ✅ supported · 🚧 in progress · ❌ not supported · — not declared

## Matrix

| Engine | Version | Type | Validate | Run | Verify | Inspect | Replay | Diff | Memory | Tools Mcp | Dag Parallel | Budget | Verification | Trace Export | Compat % | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| codex | 0.1.0 | community | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| crewai | 0.1.0 | community | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| goose | 0.1.0 | community | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| hermes | 1.0.0 | governance | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 70.8% | certified |
| langgraph | 0.1.0 | community | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| mastra | 0.1.0 | community | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| openclaw | 1.0.0 | execution | ✅ | ✅ | ✅ | ✅ | 🚧 | 🚧 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 66.7% | certified |

## Certification reports

- [`hermes`](../registry/certifications/hermes.json) — certified (70.8%)
- [`openclaw`](../registry/certifications/openclaw.json) — certified (66.7%)

## Updating this matrix

```bash
# Certify an adapter (generates registry/certifications/<name>.json)
infini certify adapters/hermes --engine infini --mock
infini certify adapters/openclaw --engine infini --mock

# Regenerate this matrix from manifests + certifications
python ci/generate_matrix.py
```

This file is auto-generated. Do not edit by hand.
