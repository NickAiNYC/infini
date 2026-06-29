# INFINI Certification Program

Three tiers of certification for adapters that conform to the INFINI spec.

---

## Tiers

### 🥉 Bronze

**Requirement:** Adapter parses Loopfiles + passes basic schema validation.

**What you get:**
- Badge on your adapter README
- Listed in the [compatibility matrix](../spec/compatibility.md) as "Bronze"
- Eligible for $500 [adapter bounty](adapter-bounty.md)

**How to earn:**
```bash
# Your adapter must have:
# - adapter.yaml with parse_loopfile: true
# - Pass infini validate on all corpus cases

infini certify adapters/my-adapter --mock
# Result: certification_status = "experimental"
```

---

### 🥈 Silver

**Requirement:** Adapter passes 80% of conformance suite + 1 production example.

**What you get:**
- "Silver" badge on your adapter README
- Listed in the [INFINI Registry](../registry/)
- Eligible for $1,000 adapter bounty (cumulative with Bronze)

**How to earn:**
```bash
# Your adapter must have:
# - parse_loopfile: true, run_loop: true, verify: true
# - Pass 80%+ of conformance tests
# - At least 1 example Loopfile that runs end-to-end

infini certify adapters/my-adapter --mock
# Result: certification_status = "compatible", compatibility >= 80%
```

---

### 🥇 Gold

**Requirement:** Adapter passes 100% conformance + 3 examples + community support.

**What you get:**
- "INFINI Certified" Gold badge
- Featured in documentation and marketplace
- Eligible for $2,000 adapter bounty (cumulative)
- Priority support from INFINI maintainers

**How to earn:**
```bash
# Your adapter must have:
# - All 6 capabilities: parse, run, verify, inspect, replay, diff
# - Pass 100% of conformance tests
# - At least 3 example Loopfiles
# - A community maintainer (not just INFINI team)

infini certify adapters/my-adapter --mock
# Result: certification_status = "certified", compatibility >= 90%
```

---

### 💎 Platinum

**Requirement:** Adapter merged into target framework's official repository.

**What you get:**
- "Platinum" badge — the highest level
- Co-marketing with INFINI
- Eligible for $5,000 adapter bounty (cumulative: $8,500 total)
- Speaking opportunities at INFINI events

**How to earn:**
Your adapter must be accepted into the target framework's official repo (e.g., `langchain-ai/langgraph` merges your INFINI adapter PR).

---

## Network effects

Every certified adapter makes INFINI more valuable. Every certified agent makes the ecosystem more portable. The registry becomes the canonical source of portable agents — like Docker Hub for agents.

```
Developer certifies adapter → gets badge → visibility → more users → more adapters → ∞
```

---

## Get started

```bash
# Read the SDK
cat sdk/README.md

# Copy the minimal adapter
cp -r sdk/minimal-adapter adapters/my-framework

# Build + certify
infini certify adapters/my-framework --mock
```

📖 **[Adapter SDK →](../sdk/)** · **[Certification Guide →](../sdk/certification-guide.md)** · **[Bounty Program →](adapter-bounty.md)**
