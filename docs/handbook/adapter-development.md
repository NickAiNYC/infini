# Adapter Development

How to build an adapter that lets any Loopfile run on your runtime.

> Someone should be able to build an adapter in under 30 minutes.

## The 30-minute path

1. Read the [Adapter SDK README](../../sdk/README.md) (5 min)
2. Copy the [minimal adapter](../../sdk/minimal-adapter/) (5 min)
3. Implement `PARSE` + `RUN` (10 min)
4. Run the [testing guide](../../sdk/testing-guide.md) (5 min)
5. Get [certified](../../sdk/certification-guide.md) (5 min)

## The 6 capabilities

| Capability | What | Required |
| --- | --- | :---: |
| `parse_loopfile` | Parse + validate | ✅ |
| `run_loop` | Execute STEPS DAG | |
| `verify` | Run checks | |
| `inspect_trace` | Emit run.json | |
| `replay` | Resume from step | |
| `diff` | Semantic diff | |

Implement them in order. Each builds on the previous.

## The manifest

Every adapter ships `adapter.yaml`:

```yaml
adapter:
  name: my-engine
  version: 0.1.0
  spec: LOOPFILE-1.0
  type: execution
capabilities:
  parse_loopfile: true
  run_loop: true
  # ...
```

## Cross-links

- [Adapter SDK](../../sdk/) — the full SDK
- [Adapter Interface Reference](../../sdk/adapter-interface.md) — the contract
- [Certification](certification.md) — get the certified badge
- [Portability](portability.md) — why adapters matter
