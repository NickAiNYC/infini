# Certification

How to get your adapter certified against the INFINI spec.

> Certification is the moat. A certified adapter is one that another
> framework can trust.

## The command

```bash
infini certify adapters/my-adapter --engine infini --mock
```

Produces `registry/certifications/my-adapter.json` + `.md`.

## The status ladder

```text
experimental  →  compatible  →  certified
  < 50%           50-89%          ≥ 90%
```

## What it tests

- Manifest exists and is valid
- Capabilities are declared honestly
- Conformance suite passes (or skips with reason)
- Compatibility percentage is computed

## Cross-links

- [Certification Guide](../../sdk/certification-guide.md) — full guide
- [Compatibility Matrix](../../spec/compatibility.md) — current status
- [Adapter Development](adapter-development.md) — build first, then certify
- [Conformance Suite](../../tests/conformance/) — the test cases
