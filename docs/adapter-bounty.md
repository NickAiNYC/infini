# INFINI Adapter Bounty Program

**Total pool:** $10,000
**Status:** Active

---

## How it works

Build an adapter that lets any Loopfile run on your framework. Get paid.

1. Pick a target framework from the list below
2. Build the adapter using the [Adapter SDK](../sdk/)
3. Submit a PR with tests + docs + at least one example Loopfile
4. Get reviewed by INFINI maintainers
5. Get paid based on certification level

---

## Bounty tiers

| Tier | Requirement | Bounty |
| --- | --- | --- |
| **Bronze** | Adapter parses Loopfiles + passes basic schema validation | $500 |
| **Silver** | Adapter passes 80% of conformance suite + 1 production example | $1,000 |
| **Gold** | Adapter passes 100% conformance + 3 examples + community support | $2,000 |
| **Platinum** | Adapter merged into target framework's official repo | $5,000 |

Bounties are cumulative — a Platinum adapter earns all four tiers ($500 + $1,000 + $2,000 + $5,000 = $8,500).

---

## Target frameworks

| Framework | Status | Bounty |
| --- | --- | --- |
| LangGraph | ⏳ Available | Up to $8,500 |
| CrewAI | ⏳ Available | Up to $8,500 |
| OpenAI Agents SDK | ⏳ Available | Up to $8,500 |
| AutoGen | ⏳ Available | Up to $8,500 |
| Mastra | ⏳ Available | Up to $8,500 |
| Claude Agent SDK | ⏳ Available | Up to $8,500 |
| Google ADK | ⏳ Available | Up to $8,500 |
| Dapr Agents | ⏳ Available | Up to $8,500 |

First adapter for each framework gets the bounty. Multiple adapters for the same framework can split the pool.

---

## How to participate

```bash
# 1. Fork the repo
git clone https://github.com/NickAiNYC/infini
cd infini

# 2. Read the SDK
cat sdk/README.md

# 3. Copy the minimal adapter
cp -r sdk/minimal-adapter adapters/my-framework

# 4. Implement the capabilities
# Edit adapters/my-framework/__init__.py

# 5. Create adapter.yaml
# Edit adapters/my-framework/adapter.yaml

# 6. Test
infini certify adapters/my-framework --mock

# 7. PR with tests + docs + example
```

---

## Rules

- Adapters must be MIT licensed
- Adapters must include proper attribution
- Adapters must pass `infini certify` at the claimed tier
- One bounty per framework (first to qualify)
- Bounties paid via GitHub Sponsors or PayPal
- INFINI maintainers review all submissions
- Decisions are final

---

## Why we're doing this

A standard becomes a standard when independent people implement it. The first external adapter is worth more than 100 internal features. This bounty program exists to cross that threshold.

[Star the repo](https://github.com/NickAiNYC/infini) · [Read the SDK](../sdk/) · [Start building](../sdk/minimal-adapter/)
