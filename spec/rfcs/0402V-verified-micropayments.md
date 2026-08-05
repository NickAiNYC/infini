# RFC-402V: Verification-Gated HTTP 402 Micropayments

```text
RFC: 402V
Title: Verification-Gated HTTP 402 Micropayments
Author: Infini Core Architecture Team
Status: Standards Track / Draft
Date: 2026-08-05
```

## 1. Abstract

This document specifies RFC-402V, an extension to the HTTP `402 Payment Required` protocol. RFC-402V binds micro-settlement releases to cryptographic execution proofs (Infini `run.json` traces), ensuring funds held in escrow are cleared only after machine output passes declared syntactic and semantic verifiers.

---

## 2. Status of This Memo

This document specifies an open, un-licenseable standards-track protocol extension for the machine-to-machine agent economy. Distribution of this memo is unlimited.

---

## 3. Headers Specification

Compliant clients and servers MUST support the following HTTP headers:

- `X-402V-Trace-Proof`: Base64-encoded, signed JSON snippet containing step execution proof.
- `X-402V-Trace-Hash`: Cryptographic SHA-256 root digest (`sha256:...`) of the full execution trace.
- `X-402V-Verifier`: URI or contract address of the verification engine validating execution.
- `X-402V-Escrow-ID`: Unique identifier for the locked payment escrow hold.

---

## 4. Protocol Flow

```text
Client (Agent)                      Provider (API / Sub-Agent)
      │                                       │
      │─────── 1. POST Request ──────────────>│
      │<────── 2. HTTP 402 + Challenge ───────│ (Header: X-402V-Challenge)
      │                                       │
[Lock Escrow]                                 │
      │─────── 3. POST + Escrow Proof ────────>│ (Header: X-402V-Escrow-ID)
      │<────── 4. HTTP 200 + Step Data ───────│
      │                                       │
[Run VERIFY]                                  │
      │                                       │
a) Pass: RELEASE ── 5a. Settle Tx ───────────>│ (Header: X-402V-Trace-Proof)
b) Fail: REFUND  ── 5b. Refund Event ─────────X (Escrow unlocked to Agent)
```

---

## 5. Trace Receipt Validation Rules

A trace receipt is valid for settlement IF AND ONLY IF:
1. `trace.outcome == "verified"`.
2. `trace.verifications` contains zero failing checks (`status == "pass"` for all entries).
3. Mean confidence across semantic verifiers meets or exceeds `confidence_threshold`.
4. `trace.loopfile_hash` matches the signed Loopfile digest.

---

## 6. Fallback & Error Behavior

- If execution produces an unverified status (`outcome != "verified"`), the client engine MUST NOT broadcast the settlement signature.
- The client engine automatically triggers `refund(escrow_id)`, releasing held funds back to the agent's available budget.
- Servers receiving invalid receipts return `HTTP 422 Unprocessable Entity`.

---

## 7. Security & Defense

- **Denial-of-Wallet (DoW) Defense**: Upfront payments are prohibited; providers receive funds only upon delivering verified execution artifacts.
- **Sybil / Extortion Prevention**: Price quotes locked during Step 2 cannot be modified mid-step.
- **Replay Protection**: `X-402V-Escrow-ID` incorporates a single-use nonce tied to `trace.started_at`.

---

## 8. Copyright Notice

Copyright (c) 2026 Infini Architecture Team. Released under the MIT License.
