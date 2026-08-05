# Agent Pay Adapter (`adapters/agent-pay`)

The **Agent Pay Adapter** extends Infini with economic governance and verification-gated settlement capabilities for autonomous AI agents.

## Architectural Overview

When an agent loop interacts with paid APIs, sub-agent services, or computational markets, Infini enforces a strict **Escrow & Verification Settlement Lifecycle**:

```
[ Step Trigger ] ──> [ Negotiate Price ] ──> [ Escrow Hold ] ──> [ Execute Step ]
                                                                       │
[ Settlement Receipt ] <── [ Release Funds ] <── [ VERIFY Checks ] <───┘
         │                                            │ (If Failed)
         └──> Emit run.json receipt                   └──> Refund Escrow
```

## Key Capabilities

1. **HTTP 402 Micropayment Negotiation**: Seamlessly parses `HTTP 402 Payment Required` headers and attaches signed payment proofs.
2. **ERC-4337 & Solana Wallet Settlement**: Direct non-custodial agent wallet interaction (`payment_method: wallet`).
3. **Verification-Gated Escrow (`settlement: hold_until_verified`)**: Funds are held prior to step execution and released *only* when `VERIFY` assertions pass (`outcome == "verified"`).
4. **Trace as Settlement Receipt**: Verified execution traces (`run.json`) automatically record cryptographic `settlement` receipts (`receipt_hash`, `tx_hash`, `settled_amount_usd`).

## Defensive Risk Mitigations

- **Algorithmic Drain**: Enforced by hard `BUDGET` dollar limits and deterministic `STOP_WHEN` predicates.
- **Denial-of-Wallet & Price Gouging**: Mitigated because payment release is strictly contingent upon verified output correctness.
- **Unbounded Loop Execution**: Prevented via trace replayability and cost accounting per step.
