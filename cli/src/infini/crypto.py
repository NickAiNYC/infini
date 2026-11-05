"""Cryptographic primitives for INFINI offline trace signing and verification.

Implements pure-Python RFC 8032 Ed25519 digital signatures with zero external
dependencies. Follows the INFINI Provenance specification (RFC-0009).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

# ── RFC 8032 Ed25519 Parameters & Arithmetic ──
_b = 256
_q = 2**255 - 19
_l = 2**252 + 27742317777372353535851937790883648493

_d = -121665 * pow(121666, _q - 2, _q) % _q
_I = pow(2, (_q - 1) // 4, _q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_d * y * y + 1, _q - 2, _q) % _q
    x = pow(xx, (_q + 3) // 8, _q)
    if (x * x - xx) % _q != 0:
        x = (x * _I) % _q
    if x % 2 != 0:
        x = _q - x
    return x


_By = 4 * pow(5, _q - 2, _q) % _q
_Bx = _xrecover(_By)
_B = [_Bx % _q, _By % _q]


def _edwards_add(P: list[int], Q: list[int]) -> list[int]:
    x1, y1 = P[0], P[1]
    x2, y2 = Q[0], Q[1]
    x3 = (x1 * y2 + x2 * y1) * pow(1 + _d * x1 * x2 * y1 * y2, _q - 2, _q) % _q
    y3 = (y1 * y2 + x1 * x2) * pow(1 - _d * x1 * x2 * y1 * y2, _q - 2, _q) % _q
    return [x3, y3]


def _scalarmult(P: list[int], e: int) -> list[int]:
    if e == 0:
        return [0, 1]
    Q = _scalarmult(P, e // 2)
    Q = _edwards_add(Q, Q)
    if e & 1:
        Q = _edwards_add(Q, P)
    return Q


def _encodeint(y: int) -> bytes:
    bits = [(y >> i) & 1 for i in range(_b)]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(_b // 8))


def _encodepoint(P: list[int]) -> bytes:
    x, y = P[0], P[1]
    bits = [(y >> i) & 1 for i in range(_b - 1)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(_b // 8))


def _decodeint(s: bytes) -> int:
    return int.from_bytes(s, "little")


def _decodepoint(s: bytes) -> list[int] | None:
    clamp = s[:31] + bytes([s[31] & 127])
    y = int.from_bytes(clamp, "little")
    x = _xrecover(y)
    if bool(x & 1) != bool(s[31] & 128):
        x = _q - x
    P = [x, y]
    # Check on curve: -x^2 + y^2 == 1 + d*x^2*y^2 (mod q)
    if (-x * x + y * y - 1 - _d * x * x * y * y) % _q != 0:
        return None
    return P


def _H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def _secret_expand(secret_key_32: bytes) -> tuple[int, bytes]:
    h = _H(secret_key_32)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= (1 << 254)
    return a, h[32:]


# ── Public API ──

def generate_keypair(seed: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate an Ed25519 private key (32 bytes) and public key (32 bytes)."""
    if seed is None:
        seed = os.urandom(32)
    elif len(seed) != 32:
        seed = hashlib.sha256(seed).digest()

    a, _ = _secret_expand(seed)
    A = _scalarmult(_B, a)
    public_key = _encodepoint(A)
    return seed, public_key


def sign_message(secret_key_32: bytes, message: bytes) -> bytes:
    """Sign message bytes with Ed25519 secret key. Returns 64-byte signature."""
    a, prefix = _secret_expand(secret_key_32)
    A = _scalarmult(_B, a)
    pub_bytes = _encodepoint(A)

    r = int.from_bytes(_H(prefix + message), "little") % _l
    R = _scalarmult(_B, r)
    R_bytes = _encodepoint(R)

    k = int.from_bytes(_H(R_bytes + pub_bytes + message), "little") % _l
    S = (r + k * a) % _l
    return R_bytes + _encodeint(S)


def verify_message(public_key_32: bytes, message: bytes, signature_64: bytes) -> bool:
    """Verify an Ed25519 signature over message bytes. Returns True if valid."""
    if len(public_key_32) != 32 or len(signature_64) != 64:
        return False

    A = _decodepoint(public_key_32)
    if A is None:
        return False

    R_bytes = signature_64[:32]
    S_bytes = signature_64[32:]

    R = _decodepoint(R_bytes)
    if R is None:
        return False

    S = _decodeint(S_bytes)
    if S >= _l:
        return False

    k = int.from_bytes(_H(R_bytes + public_key_32 + message), "little") % _l
    # Check S*B == R + k*A
    SB = _scalarmult(_B, S)
    kA = _scalarmult(A, k)
    RkA = _edwards_add(R, kA)

    return SB == RkA


def canonical_trace_hash(trace_data: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of trace payload (excluding dynamic signatures)."""
    clean_dict = dict(trace_data)
    # Strip existing signatures and dynamic hashes to prevent circular hash
    if "provenance" in clean_dict and isinstance(clean_dict["provenance"], dict):
        clean_prov = dict(clean_dict["provenance"])
        clean_prov.pop("engine_signature", None)
        clean_prov.pop("public_key", None)
        clean_prov.pop("canonical_hash", None)
        clean_dict["provenance"] = clean_prov

    canonical_json = json.dumps(clean_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def get_or_create_default_keypair() -> tuple[bytes, bytes]:
    """Load or generate the user's default Ed25519 signing keypair in ~/.infini/keys/."""
    key_dir = Path.home() / ".infini" / "keys"
    key_dir.mkdir(parents=True, exist_ok=True)
    priv_path = key_dir / "ed25519.key"
    pub_path = key_dir / "ed25519.pub"

    if priv_path.exists() and pub_path.exists():
        priv_bytes = bytes.fromhex(priv_path.read_text().strip())
        pub_bytes = bytes.fromhex(pub_path.read_text().strip())
        return priv_bytes, pub_bytes

    priv_bytes, pub_bytes = generate_keypair()
    priv_path.write_text(priv_bytes.hex())
    pub_path.write_text(pub_bytes.hex())
    return priv_bytes, pub_bytes


def sign_trace_dict(trace_data: dict[str, Any], secret_key: bytes | None = None) -> tuple[dict[str, Any], str, str]:
    """Sign a trace dictionary in-place. Returns (updated_dict, signature_hex, pubkey_hex)."""
    if secret_key is None:
        secret_key, pub_key = get_or_create_default_keypair()
    else:
        _, pub_key = generate_keypair(secret_key)

    h_hex = canonical_trace_hash(trace_data)
    sig_bytes = sign_message(secret_key, h_hex.encode("utf-8"))
    sig_hex = sig_bytes.hex()
    pub_hex = pub_key.hex()

    if "provenance" not in trace_data or not isinstance(trace_data["provenance"], dict):
        trace_data["provenance"] = {}

    trace_data["provenance"]["engine_signature"] = f"ed25519:{sig_hex}"
    trace_data["provenance"]["public_key"] = f"ed25519:{pub_hex}"
    trace_data["provenance"]["canonical_hash"] = f"sha256:{h_hex}"

    return trace_data, sig_hex, pub_hex


def verify_trace_dict(trace_data: dict[str, Any], expected_pubkey_hex: str | None = None) -> tuple[bool, str]:
    """Verify the Ed25519 signature on an INFINI trace dict.
    
    Returns (is_valid, reason).
    """
    prov = trace_data.get("provenance", {})
    if not isinstance(prov, dict):
        return False, "Missing or malformed provenance block"

    sig_str = prov.get("engine_signature", "")
    if not sig_str.startswith("ed25519:"):
        return False, f"Missing or unsupported signature format: {sig_str}"
    sig_hex = sig_str.split("ed25519:")[1].strip()

    pub_str = expected_pubkey_hex or prov.get("public_key", "")
    if pub_str.startswith("ed25519:"):
        pub_str = pub_str.split("ed25519:")[1].strip()

    if not pub_str:
        return False, "No public key provided or found in trace"

    try:
        sig_bytes = bytes.fromhex(sig_hex)
        pub_bytes = bytes.fromhex(pub_str)
    except Exception as e:
        return False, f"Hex decode error: {e}"

    h_hex = canonical_trace_hash(trace_data)
    valid = verify_message(pub_bytes, h_hex.encode("utf-8"), sig_bytes)
    if valid:
        return True, f"Valid Ed25519 signature for sha256:{h_hex}"
    return False, "Signature verification failed (mismatch or corrupted payload)"
