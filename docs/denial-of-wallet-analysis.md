# Why Agent Wallets Lose Millions to Denial-of-Wallet (DoW) Attacks — And How RFC-402V Fixes It

> **Author**: Infini Core Architecture Team  
> **Published**: August 2026  
> **Specification**: [RFC-402V](file:///Users/nick/infini/spec/rfcs/0402V-verified-micropayments.md)

---

## 1. The Autonomous Agent Economic Vulnerability

As AI agents transition from sandboxed chat assistants into autonomous economic operators equipped with non-custodial crypto wallets (e.g., via x402, Solana agent accounts, ERC-4337 bundlers, or virtual cards), they introduce an entirely new threat model: **Denial-of-Wallet (DoW)** attacks.

Unlike conventional Denial-of-Service (DoS) attacks—which aim to exhaust server CPU or bandwidth—Denial-of-Wallet attacks target the financial balance of an autonomous agent by tricking its purchasing engine into settling real money for zero, incomplete, or hallucinated software output.

---

## 2. The Flaw in Existing Micropayment Protocols (x402 & Agent Cards)

Protocols like x402 settle transactions *during* the initial HTTP request-response handshake:

```text
[Agent] ────────── 1. HTTP POST ──────────> [Predatory API Server]
[Agent] <───────── 2. HTTP 402 ($1.00) ──── [Predatory API Server]
[Agent] ─ 3. Settle Payment Upfront ($1) ─> [Predatory API Server]
[Agent] <───────── 4. HTTP 200 (Garbage) ── [Predatory API Server]
```

### Why This Fails:
1. **Blind Pre-Payment**: The payment is finalized **before** the client receives or parses the payload.
2. **Zero Quality Guarantee**: The API provider can return invalid JSON, truncated responses, or empty arrays without financial penalty.
3. **Recursive Drain**: If an agent is operating in an unmonitored loop, a single predatory endpoint can drain $1,000 in seconds by returning HTTP 402 challenges in rapid succession.

---

## 3. The Solution: Verification-Gated Escrow (RFC-402V)

RFC-402V shifts the settlement paradigm from **"Pay to Access"** to **"Settle Upon Verified Correctness"**:

```text
[Agent] ────────── 1. HTTP POST ──────────> [API Provider]
[Agent] <───────── 2. HTTP 402 ($1.00) ──── [API Provider]
[Hold Escrow]
[Agent] ────────── 3. Submit Escrow Proof ─> [API Provider]
[Agent] <───────── 4. Return Output ──────── [API Provider]
[Run VERIFY]
  ├── Pass ───────> Release Escrow ($1.00)
  └── Fail ───────> REFUND Escrow ($0.00 Lost)
```

---

## 4. Architectural Implementation & Trace Receipts

Under RFC-402V, every agent step execution is recorded in a portable trace (`run.json`). When execution completes, Infini runs:
- **Syntactic Verifiers**: Deterministic exit code, JSON schema, and linter checks.
- **Semantic Verifiers**: Model-judged confidence scores evaluated against task rubrics.

Only when all verifiers pass (`outcome == "verified"`) does Infini generate a signed settlement receipt:

```json
{
  "loopfile": "market-research-agent@1.0.0",
  "outcome": "verified",
  "settlement": {
    "status": "settled",
    "settled_amount_usd": 1.00,
    "payment_method": "http402",
    "receipt_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "tx_hash": "0x402_tx_9b4a1c0d2e8f"
  }
}
```

If the endpoint serves garbage, `VERIFY` fails, the escrow hold is released, and 100% of the funds are refunded to the agent's budget.

---

## 5. Conclusion

The future of the machine economy requires software to buy software—but **only after the work is proven correct**. RFC-402V provides the un-licenseable, verification-gated settlement primitive that secures autonomous wallets against Denial-of-Wallet exploitation.

Try the benchmark live:
```bash
python3 -m infini.benchmark.vulnerability
```
