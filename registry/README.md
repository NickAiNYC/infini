# INFINI Loop Registry

> **The catalog for portable intelligence.**
>
> Docker had Hub. npm had Registry. INFINI has the Loop Registry — the world's first catalog of portable, verifiable, framework-agnostic agent loops.

---

## What is it?

The INFINI Loop Registry is a catalog of agent Loopfiles that work on any framework. Like Docker Hub for containers or npm for JavaScript, the Loop Registry lets you discover, share, and install agent logic that runs on LangGraph, CrewAI, OpenAI Agents SDK, or your own runtime.

Every loop is verified against the INFINI conformance suite, cryptographically signed, and comes with replayable traces.

**Write once. Publish once. Run anywhere.**

---

## CLI Commands

```bash
# Search
infini registry search "rag agent" --framework langgraph --tier gold

# Install
infini registry install @infini/research-agent@1.0

# Publish
infini registry publish ./Loopfile --namespace @my-org --verify

# Authentication
infini registry login --token <token>
infini registry whoami

# Info
infini registry info @infini/research-agent

# Pack for offline/air-gapped
infini registry pack ./my-loop/ --output my-loop.loop
```

---

## Architecture

The "Git + CAS" Hybrid Model:

| Layer | Technology | Purpose |
| --- | --- | --- |
| Index | Git repo | Human-readable metadata, PR-based submissions |
| Blob Storage | S3/R2/GCS (content-addressed by SHA256) | Loopfiles, traces, large assets |
| Metadata Cache | SQLite (read-through) | Fast search, browse, API responses |
| Auth | GitHub OAuth + API tokens | Identity, permissions, rate limiting |

### Loop Package structure

```
Loop Package v1
├── manifest.json              # Metadata (name, version, author, license)
├── loop.yaml                  # The Loopfile
├── loop.sig                   # Ed25519 signature
├── verification/
│   ├── conformance.json       # Conformance suite results
│   ├── benchmarks.json        # Performance metrics
│   └── traces/                # Replayable trace files
├── dependencies/
│   ├── mcp-tools.json         # MCP tool dependencies
│   └── skills/                # Anthropic Skills (optional)
├── examples/
│   └── example-usage.yaml
└── README.md
```

### Manifest Schema

📖 **[manifest-schema.json](manifest-schema.json)** — the JSON Schema for Loop Package manifests.

### Registry API

📖 **[openapi.yaml](openapi.yaml)** — the full OpenAPI 3.0 specification.

Base URL: `https://registry.infini.dev/v1/`

Key endpoints:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/loops` | GET | Search loops |
| `/loops/{ns}/{name}` | GET | Get loop metadata |
| `/loops/{ns}/{name}/{ver}/loopfile` | GET | Download Loopfile |
| `/loops` | POST | Publish new loop |
| `/loops/{ns}/{name}/{ver}/verify` | POST | Run verification |
| `/namespaces` | GET | List namespaces |
| `/auth/verify` | GET | Verify token |

---

## Security Model

| Layer | Mechanism | Purpose |
| --- | --- | --- |
| Identity | GitHub OAuth + Ed25519 keypairs | Who published? |
| Integrity | SHA256 content addressing + loop.sig | Was it tampered with? |
| Verification | Conformance suite runs on publish | Does it work? |
| Reproducibility | Time-travel traces included | Can I replay and trust? |
| Attestation | Signed verification reports | Who verified it? |

---

## Certification Tiers

| Tier | Requirement | Badge |
| --- | --- | --- |
| 🥉 Bronze | Passes schema validation | Listed in registry |
| 🥈 Silver | 80%+ conformance + 1 trace | "Verified" badge |
| 🥇 Gold | 100% conformance + 3 traces + benchmarks | "Certified" badge + featured |
| 💎 Platinum | Gold + 1,000+ installs + community | "Premium" badge + homepage |

📖 **[Certification Program →](../docs/certification-program.md)**

---

## Self-Hosting

```bash
# Minimal (SQLite + single binary)
curl -fsSL https://get.infini.dev/registry | bash
infini registry serve --port 8080 --storage ./data

# Production (PostgreSQL + S3)
docker run -d \
  -p 8080:8080 \
  -e DATABASE_URL=postgres://... \
  -e STORAGE=s3://my-bucket/ \
  infini/registry:latest
```

### Private registry config

```yaml
# ~/.infini/registry.yaml
default: https://registry.infini.dev
registries:
  public: https://registry.infini.dev
  acme-corp: https://registry.internal.acme.com
  dev: http://localhost:8080
```

### Air-gapped installation

```bash
# Export loops from public registry
infini registry pack ./my-loops/ --output loops.tar.gz

# Import into air-gapped instance
infini registry unpack loops.tar.gz --target ./registry-data/
```

---

## Network Effect

```
More publishers → More loops → More users → More installs
        ↑                                          ↓
   More adapters ← More frameworks ← More demand ← More verification
```

Every loop published makes INFINI more valuable. Every adapter built makes more loops portable. Every install proves the network effect.

---

## Status

- **Phase 1 (current):** CLI commands implemented (search, install, publish, login, info, pack). Local cache works. Remote registry API spec published.
- **Phase 2 (planned):** Public registry at `registry.infini.dev`. Web UI for discovery.
- **Phase 3 (future):** Semantic search, analytics, private orgs, self-hosting guide.

---

## See also

- [Manifest Schema](manifest-schema.json)
- [OpenAPI Spec](openapi.yaml)
- [Registry Protocol](protocol.md)
- [Metadata Schema](metadata-schema.md)
- [Certification Program](../docs/certification-program.md)
- [Adapter Bounty](../docs/adapter-bounty.md)
