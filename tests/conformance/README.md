# INFINI Conformance Test Suite

Every adapter must pass the same tests. This is the certification layer.

> Modeled on OCI's conformance tests for container runtimes and
> OpenAPI's validators. An adapter that passes this suite is eligible
> for a ✅ in the compatibility matrix.

---

## The 8 conformance loops

| Loop | What it tests |
| --- | --- |
| [`simple-loop`](simple-loop/) | Basic parse + run + verify. The "hello world" of Loopfiles. |
| [`retry-loop`](retry-loop/) | Step-level retry with exponential backoff. |
| [`verification-loop`](verification-loop/) | Two-tier verification: syntactic + semantic, with confidence threshold. |
| [`cost-loop`](cost-loop/) | Budget enforcement: dollars, minutes, tokens. |
| [`memory-loop`](memory-loop/) | LESSONS block: append after run, recall before run. |
| [`parallel-loop`](parallel-loop/) | Parallel workers via `depends_on` DAG. |
| [`research-loop`](research-loop/) | Multi-step research with citation verification. |
| [`browser-loop`](browser-loop/) | Browser tool calls (OpenClaw-style). |

Each loop has:
- `Loopfile.yaml` — the loop to test.
- `expected.json` — the expected trace shape (outcome, step count, verification results).

---

## Running the suite

```bash
# Run against the INFINI Reference Engine
infini conformance tests/conformance/ --engine infini

# Run against an adapter
infini conformance tests/conformance/ --engine hermes
infini conformance tests/conformance/ --engine openclaw
```

The runner:
1. For each loop, runs `infini run` with `--mock`.
2. Loads the resulting trace.
3. Compares against `expected.json`.
4. Reports pass/fail per loop.

---

## Conformance levels

| Level | What's required |
| --- | --- |
| **Parse** | Adapter can parse all 8 Loopfiles without error. |
| **Run** | Adapter can execute all 8 loops and produce a trace. |
| **Verify** | Adapter's verification results match `expected.json`. |
| **Inspect** | Adapter's traces can be loaded by `infini inspect`. |
| **Replay** | Adapter supports `infini replay --step` on all 8 loops. |
| **Diff** | Adapter supports `infini diff` between Loopfile versions. |

An adapter's conformance row in [`spec/compatibility.md`](../../spec/compatibility.md) reflects the highest level it passes.

---

## Certification

An adapter that passes all 6 levels on all 8 loops earns the
**INFINI Certified** badge:

```
✓ INFINI Certified
  Loopfile v1.0
  Replay · Verification · Artifacts
  Cost accounting · Memory snapshots · Trace export
```

Certified adapters are listed in [`spec/compatibility.md`](../../spec/compatibility.md) with the badge.

---

## Adding a new conformance loop

1. Create a directory under `tests/conformance/<name>/`.
2. Add `Loopfile.yaml` — the loop.
3. Add `expected.json` — the expected trace shape.
4. PR to `tests/conformance/`.

The conformance suite is additive. New loops don't break existing adapters; they just test more.

---

## License

MIT. See [repository LICENSE](../../LICENSE).
