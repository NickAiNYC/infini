# Certification Guide

How to get your adapter certified against the INFINI spec.

> Certification is the moat. A certified adapter is one that another
> framework can trust to behave correctly.

---

## What certification means

`infini certify` runs your adapter against the conformance suite and
produces a report with:

- **Supported capabilities** — declared in your `adapter.yaml`
- **Conformance results** — pass/fail/skip per test case
- **Compatibility percentage** — 50% capabilities + 50% conformance
- **Certification status**:
  - `experimental` — < 50% compatibility, or missing required caps
  - `compatible` — 50-89% compatibility
  - `certified` — ≥ 90% compatibility + all required caps pass

---

## How to certify

```bash
infini certify adapters/my-adapter --engine infini --mock
```

This produces:

```
registry/certifications/my-adapter.json   ← machine-readable
registry/certifications/my-adapter.md     ← human-readable
```

The JSON report:

```json
{
  "adapter_name": "my-adapter",
  "version": "0.1.0",
  "engine": "infini",
  "spec_version": "LOOPFILE-1.0",
  "supported_capabilities": ["parse_loopfile", "run_loop", "verify"],
  "conformance_results": [
    { "test_name": "simple-loop", "status": "pass", "detail": "..." },
    { "test_name": "retry-loop", "status": "skip", "detail": "missing: replay" }
  ],
  "compatibility_percentage": 75.0,
  "certification_status": "compatible",
  "timestamp": "2026-06-28T17:16:35Z"
}
```

---

## The certification ladder

```text
experimental  →  compatible  →  certified
     ↑                ↑              ↑
  < 50%           50-89%          ≥ 90%
  or missing      + required      + all required
  required        caps pass       caps pass
```

### experimental (starting point)

Most new adapters start here. You've declared capabilities but haven't
implemented enough to pass conformance. That's fine — you're visible in
the matrix, marked `experimental`, and contributors can see what's
missing.

### compatible (mid-point)

You implement PARSE + RUN + VERIFY + INSPECT. Conformance passes on most
cases. You're listed as `compatible` in the matrix. Teams can use your
adapter with confidence for most loops.

### certified (the goal)

You implement all 6 capabilities. Conformance passes on all cases. You're
listed as `certified` in the matrix with a compatibility percentage.
This is the badge that makes other frameworks trust you.

---

## What the conformance suite tests

The suite has 8 cases, each targeting a different capability:

| Case | Tests |
| --- | --- |
| `simple-loop` | PARSE + RUN on a minimal loop |
| `retry-loop` | RUN with retry policy |
| `verification-loop` | VERIFY with two-tier checks |
| `cost-loop` | BUDGET enforcement |
| `memory-loop` | LESSONS block |
| `parallel-loop` | DAG scheduling |
| `research-loop` | Multi-step + browser tools |
| `browser-loop` | Browser tool calls |

If your adapter doesn't support a capability required by a case, that
case is marked `skip` (not `fail`). Skips don't hurt your percentage as
much as fails.

---

## Regenerating the compatibility matrix

After certifying, regenerate the matrix:

```bash
python ci/generate_matrix.py
```

This updates `spec/compatibility.md` with your adapter's new status and
compatibility percentage.

---

## When to re-certify

Re-certify when:
- You add a new capability (flip a `false` to `true` in `adapter.yaml`)
- You fix a bug that was causing conformance failures
- You bump your adapter version
- The spec revs (rare — minor versions are additive)

Certification is not permanent. The matrix is regenerated from the
latest certification reports. If you stop maintaining your adapter, it
stays listed but its compatibility percentage reflects the last
certification.

---

## Certification in CI

Add certification to your adapter's CI:

```yaml
# .github/workflows/adapter-ci.yml
- name: Certify
  run: |
    pip install -e './cli[dev]'
    infini certify adapters/my-adapter --engine infini --mock
```

This ensures every PR re-runs certification and updates the report.

---

## Next steps

- [Publishing Guide](publishing-guide.md) — share your certified adapter
- [Testing Guide](testing-guide.md) — test before you certify
- [Compatibility matrix](../spec/compatibility.md) — see where you stand
