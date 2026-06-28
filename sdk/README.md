# INFINI Adapter SDK

Build an adapter that lets any Loopfile run on your runtime. Someone
should be able to build one in under 30 minutes.

> **Would this make another framework want to support INFINI?**
> That's the guiding question for every decision in this SDK.

---

## What is an adapter?

An adapter is a thin module that translates Loopfile primitives into
your runtime's native operations. INFINI owns the format; your engine
owns the execution. The adapter is the bridge.

A Loopfile declares **what** to do (steps, agents, verification). The
adapter decides **how** to do it on your runtime.

---

## The 6 capabilities

Every adapter declares which capabilities it implements. Partial
conformance is allowed and tracked honestly in the
[compatibility matrix](../spec/compatibility.md).

| Capability | What it does | Required to be listed |
| --- | --- | :---: |
| `parse_loopfile` | Parse and validate a Loopfile | ✅ |
| `run_loop` | Execute the STEPS DAG | |
| `verify` | Run syntactic + semantic checks | |
| `inspect_trace` | Emit a `run.json` trace | |
| `replay` | Resume from any step | |
| `diff` | Semantic diff between Loopfiles | |

`parse_loopfile` is the only required capability. An adapter that ships
only PARSE is registered and listed; it can validate Loopfiles but not
run them.

---

## Build an adapter in 30 minutes

1. **Read the [Adapter Interface Reference](adapter-interface.md)** (5 min)
2. **Copy the [minimal adapter](minimal-adapter/)** (5 min)
3. **Implement `PARSE` + `RUN`** (10 min)
4. **Run the [testing guide](testing-guide.md)** (5 min)
5. **Get [certified](certification-guide.md)** (5 min)
6. **[Publish](publishing-guide.md) to the registry** (optional)

---

## SDK structure

```
sdk/
├── README.md                    ← you are here
├── adapter-interface.md         ← normative interface reference
├── minimal-adapter/             ← copy this as your starting point
│   ├── adapter.yaml             ← manifest template
│   ├── __init__.py              ← ~50-line PARSE-only adapter
│   └── README.md                ← how to extend it
├── testing-guide.md             ← how to test your adapter
├── certification-guide.md       ← how to get certified
└── publishing-guide.md          ← how to publish to the registry
```

---

## The adapter manifest

Every adapter ships an `adapter.yaml` manifest:

```yaml
adapter:
  name: my-engine
  version: 0.1.0
  spec: LOOPFILE-1.0
  type: execution          # governance | execution | hybrid
  description: My agent runtime.

engine:
  type: my-engine
  runtime: my-engine-runtime
  min_version: 1.0.0

capabilities:
  parse_loopfile: true
  run_loop: true
  verify: true
  inspect_trace: true
  replay: false            # planned
  diff: false              # planned

install:
  pip: infini-cli[my-engine]

repo: https://github.com/you/infini-my-engine
```

The manifest is what `infini engines` and `infini certify` read. Without
it, your adapter is invisible.

---

## The lifecycle

```text
1. PARSE     — read the Loopfile, validate against schema
2. RUN       — execute the STEPS DAG with declared AGENTS
3. VERIFY    — run syntactic + semantic checks, compute confidence
4. INSPECT   — emit a run.json trace
5. REPLAY    — restore state at any step, resume from there
6. DIFF      — semantic diff between two Loopfiles
```

You can implement these in order. Each builds on the previous. An adapter
that implements PARSE + RUN + VERIFY + INSPECT is "compatible"; one that
adds REPLAY + DIFF is "certified."

---

## Semantic versioning

Adapters version independently of the spec:

- **Patch** (`0.1.0` → `0.1.1`): bug fixes, no new capabilities
- **Minor** (`0.1.0` → `0.2.0`): new capabilities, backward-compatible
- **Major** (`0.1.0` → `1.0.0`): breaking changes to adapter behavior

The `spec` field in your manifest declares which spec version you
support. It must match the `LOOPFILE` version in the Loopfiles you
accept. See [spec versioning](../spec/versions.md).

---

## Next steps

- [Adapter Interface Reference](adapter-interface.md) — the normative contract
- [Minimal Adapter](minimal-adapter/) — copy and extend
- [Testing Guide](testing-guide.md) — verify your adapter works
- [Certification Guide](certification-guide.md) — get the certified badge
- [Publishing Guide](publishing-guide.md) — share your adapter with the ecosystem

---

## License

MIT. See [repository LICENSE](../LICENSE).
