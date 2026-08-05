# Agent Pay: Economic Governance & Settlement for Autonomous AI Agents

> **Infini turns autonomous agent work into a portable, verifiable, and settleable unit of economic activity.**
> **Software buys software only after the work is proven correct.**

---

## 1. Executive Summary

As AI agents evolve into autonomous economic actors holding non-custodial wallets and querying paid APIs, traditional billing models (per-seat monthly SaaS, credit cards) collapse. 

Infini introduces **Agent Pay**—native payment and economic governance primitives integrated directly into the portable `Loopfile` specification (`LOOPFILE: "1.0"`).

---

## 2. Defensive Primitives Against Autonomous Risk

| Risk Pattern | Attack Vector | Infini Defensive Primitive |
| :--- | :--- | :--- |
| **Algorithmic Drain** | Runaway recursive LLM loops consuming thousands of dollars in minutes. | Strict `BUDGET` ceilings (dollars, minutes, tokens) + deterministic `STOP_WHEN` predicates. |
| **Denial-of-Wallet (DoW)** | Malicious or degraded APIs charging upfront fees for garbage data or inflated responses. | `settlement: hold_until_verified` escrow lock; funds released only upon passing `VERIFY` assertions. |
| **Unbounded Execution** | Opaque agent steps with non-deterministic costs and no audit trail. | Trace-backed settlement receipts (`run.json`) recording every step, cost, and verification proof. |

---

## 3. Loopfile Specification (`BUDGET` Extension)

```yaml
LOOPFILE: "1.0"
name: market-research-agent
version: 1.0.0
OBJECTIVE: "Gather competitor API pricing and synthesize report."

AGENTS:
  - { name: researcher, role: researcher, model_tier: sonnet }

STEPS:
  - { id: s1, name: query_paid_api, action: fetch_market_data, uses: researcher }

VERIFY:
  syntactic: ["report.json:valid_schema"]
  semantic: ["judge:freshness>=90"]
  confidence_threshold: 85

BUDGET:
  dollars: 15
  minutes: 10
  payment_method: http402            # wallet | api_key | http402
  settlement: hold_until_verified    # hold_until_verified | immediate
  wallet_address: "0x402_agent_wallet_7f3b"

STOP_WHEN: ["all_verify_passed"]
```

---

## 4. Escrow & Settlement Lifecycle

1. **Price Negotiation**: Pre-execution HTTP 402 challenge negotiation or cost estimation.
2. **Escrow Hold**: `AgentPayAdapter` locks step cost against declared `BUDGET`.
3. **Step Execution**: Agent executes task and emits artifacts.
4. **Verification Gate**: Engine evaluates `VERIFY` syntactic and semantic checks.
5. **Settlement / Refund**:
   - **`outcome == "verified"`**: Escrow funds are released to provider, cryptographic `receipt_hash` and `tx_hash` are logged.
   - **`outcome != "verified"`**: Escrow funds are unlocked and returned to agent budget.

---

## 5. Machine-Readable Settlement Receipts (`run.json`)

When a run achieves `outcome: "verified"`, the emitted `run.json` acts as an invoice and cryptographic settlement receipt:

```json
{
  "loopfile": "market-research-agent@1.0.0",
  "outcome": "verified",
  "budget": {
    "spent_dollars": 1.50,
    "spent_minutes": 2.1,
    "payment_method": "http402"
  },
  "settlement": {
    "status": "settled",
    "settled_amount_usd": 1.50,
    "payment_method": "http402",
    "wallet_address": "0x402_agent_wallet_7f3b",
    "settlement_rule": "hold_until_verified",
    "receipt_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "tx_hash": "0x402_tx_9b4a1c0d2e8f"
  }
}
```
