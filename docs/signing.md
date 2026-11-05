# Cryptographic Trace Signing & Verification

INFINI supports local Ed25519 cryptographic signing of execution traces. This ensures offline provenance, tamper resistance, and auditability: any party can independently verify that a run trace (`run.json`) was executed by a specific keyholder without calling remote APIs or trusting third-party loggers.

---

## How It Works

1. **Canonical Hashing:**
   The trace dictionary is canonicalized (keys sorted, whitespace stripped, dynamic signature fields stripped to prevent circularity). A SHA-256 digest is computed over this canonical representation.
2. **Ed25519 Signature:**
   The SHA-256 digest string is signed using standard RFC 8032 Ed25519 private key arithmetic (implemented in pure Python with zero external dependencies).
3. **Provenance Envelope:**
   The resulting signature and public key are embedded directly into the trace's `provenance` block:
   ```json
   {
     "provenance": {
       "engine_signature": "ed25519:<64-byte hex signature>",
       "public_key": "ed25519:<32-byte hex public key>",
       "canonical_hash": "sha256:<sha256 hex digest>"
     }
   }
   ```

---

## Signing a Run

Pass the `--sign` flag to `infini run`:

```bash
infini run examples/quickstart.yaml --sign
```

By default, INFINI uses or creates an Ed25519 keypair at `~/.infini/keys/ed25519.key` (public key: `~/.infini/keys/ed25519.pub`).

---

## Offline Verification Command

To verify a trace offline without network access:

```bash
infini verify-trace runs/latest/run.json
```

Example output:
```text
✓ Trace signature is VALID
  Signer: ed25519:7b1057af3afa9f4876f084a320e2e3df2800e4015b169ec5ebd2da1477f9032e
  Detail: Valid Ed25519 signature for sha256:a46ea67580837550486a7aeb5bbc5fecfb0a6e4cb4b5e26e99ea175a02d463d7
```

To verify against an explicit expected public key:
```bash
infini verify-trace runs/latest/run.json --key <public-key-hex>
```

If any field in the trace has been tampered with (outcomes modified, step metrics forged, token numbers altered), verification immediately fails:
```text
✗ Trace signature is INVALID
  Reason: Signature verification failed (mismatch or corrupted payload)
```

---

## External Verifier Interface Specification

External verification tools, ledger connectors, or downstream verification engines consume this interface via standard JSON-schema inputs:

1. **Input Payload:** JSON trace with `provenance.engine_signature` and `provenance.public_key`.
2. **Hash Computation:**
   - Exclude `provenance.engine_signature`, `provenance.public_key`, and `provenance.canonical_hash`.
   - Serialize with `sort_keys=True` and no whitespace separators (`separators=(",", ":")`).
   - Compute `SHA-256(canonical_bytes)`.
3. **Signature Validation:**
   - Verify `Ed25519Verify(pubkey, hash_ascii_bytes, signature) == true`.
