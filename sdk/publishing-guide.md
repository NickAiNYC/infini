# Publishing Guide

How to publish your adapter to the INFINI registry.

> The registry is Git-based. No hosted service. Your adapter lives in
> a directory; the registry is just a structured index.

---

## Where adapters live

```
registry/
├── official/         ← INFINI team maintained (hermes, openclaw)
├── community/        ← community maintained, certified
└── experimental/     ← community maintained, not yet certified
```

Your adapter goes in `registry/community/` once certified, or
`registry/experimental/` while in development.

---

## The registry entry

Each adapter has a directory in the registry:

```
registry/community/my-adapter/
├── manifest.yaml        ← adapter metadata + capabilities
├── metadata.json        ← owner, license, links
├── README.md            ← what the adapter does
├── compatibility.json   ← latest certification report
└── examples/
    └── my-loop.yaml     ← at least one runnable example
```

---

## manifest.yaml

```yaml
adapter:
  name: my-adapter
  version: 0.1.0
  spec: LOOPFILE-1.0
  type: execution
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
  replay: false
  diff: false

install:
  pip: infini-cli[my-adapter]

repo: https://github.com/you/infini-my-adapter
```

---

## metadata.json

```json
{
  "name": "my-adapter",
  "owner": {
    "name": "Your Name",
    "github": "yourusername",
    "email": "you@example.com"
  },
  "license": "MIT",
  "status": "community",
  "supported_engines": ["my-engine"],
  "spec_version": "LOOPFILE-1.0",
  "last_certification": "2026-06-28T17:16:35Z",
  "certification_status": "compatible",
  "compatibility_percentage": 75.0,
  "repo": "https://github.com/you/infini-my-adapter",
  "homepage": "https://github.com/you/infini-my-adapter",
  "tags": ["execution", "browser", "terminal"]
}
```

---

## README.md

Your adapter's README should answer:

1. **What does this adapter do?** (one paragraph)
2. **What runtime does it wrap?** (link to the runtime)
3. **What capabilities are supported?** (the matrix row)
4. **How do I install it?** (`pip install infini-cli[my-adapter]`)
5. **How do I use it?** (`infini run loop.yaml --engine my-adapter`)
6. **Where's the source?** (link to your repo)
7. **How do I report bugs?** (link to issues)

---

## Publishing steps

1. **Build your adapter** — follow the [SDK README](README.md)
2. **Test it** — run the [testing guide](testing-guide.md)
3. **Certify it** — run the [certification guide](certification-guide.md)
4. **Create the registry entry**:
   ```bash
   mkdir -p registry/community/my-adapter/examples
   # Copy your adapter.yaml, write metadata.json, README.md, examples/
   ```
5. **PR to `registry/community/`** (or `registry/experimental/` if not yet certified)
6. **A maintainer reviews** — checks your certification report is honest, your manifest matches your actual capabilities
7. **Merged** — your adapter appears in `infini engines` and the compatibility matrix

---

## Versioning your published adapter

When you update your adapter:

1. Bump the version in `manifest.yaml` and `metadata.json`
2. Re-run `infini certify` to generate a fresh `compatibility.json`
3. PR the updated files

The registry is append-only by version. Old versions stay listed so
users can pin to a known-good version.

---

## What we look for in review

- **Honest capabilities.** Don't declare `replay: true` if you haven't
  implemented it. The conformance suite will catch you.
- **Working examples.** At least one example Loopfile that runs.
- **Clear README.** A stranger should understand your adapter in 30 seconds.
- **Real owner.** Use your real GitHub handle. We want to credit you.

---

## What we reject

- Adapters that declare capabilities they don't implement
- Adapters with no examples
- Adapters with no owner information
- Adapters that wrap proprietary/closed runtimes without permission

---

## Next steps

- [Adapter Interface Reference](adapter-interface.md) — the contract
- [Certification Guide](certification-guide.md) — get certified first
- [SDK README](README.md) — start here
