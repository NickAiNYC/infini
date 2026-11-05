# Unproven Concepts & Future Ideas Archive

This document collects architectural concepts, exploratory features, and aspirational benchmarks that were previously referenced in early experimental drafts but have not yet been independently verified with reproducible benchmarks or production implementations.

Per Rule Zero of INFINI:
> Every claim in documentation must be backed by a command a stranger can run in under 5 minutes. If it cannot be proven today, it lives here until verified.

---

## 1. Concurrency: "50+ Agents on a t3.micro"
- **Original Claim:** Single-node SQLite in WAL mode can coordinate 50+ concurrent agents on an AWS `t3.micro` instance (2 vCPU, 1 GB RAM) with sub-100ms scheduling latency.
- **Current Reality:** SQLite WAL mode handles local thread/process concurrency well, but multi-agent queue throughput under high contention on constrained burstable instances has not been systematically stress-tested with reproducible load harnesses.
- **Path to Verification:** Build a synthetic load harness in `benchmarks/` simulating 50 concurrent agent processes performing transactional task claiming, heartbeat writes, and trace logging against SQLite WAL mode on resource-constrained containers.

---

## 2. Agent Pay & Escrow Protocol
- **Original Claim:** Native HTTP 402, ERC-4337, and Solana wallet settlement with `settlement: hold_until_verified` cryptographic escrow locks.
- **Current Reality:** An experimental mock adapter existed (`adapters/agent-pay`), but live blockchain or payment-gateway settlement was never wired to actual RPC endpoints or audited on-chain smart contracts.
- **Path to Verification:** Implement verifiable payment receipts with real testnet integrations (e.g. Sepolia or Solana Devnet) or off-chain signed state channels, backed by full transaction verification.

---

## 3. 3D Spatial Trace Observatory
- **Original Claim:** Real-time 3D web-based execution graph visualizer built with Next.js and React Three Fiber.
- **Current Reality:** `observatory-ui/` contains a prototype frontend with mock WebGL canvas components, but live trace streaming and production WebSocket ingestion are not complete.
- **Path to Verification:** Implement OpenTelemetry / WebSocket ingestion into a lightweight frontend renderer, tested end-to-end against live run traces.
