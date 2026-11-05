"""Tests for Ed25519 trace signing and offline verification."""
import json
from pathlib import Path
import pytest

from infini.crypto import (
    generate_keypair,
    sign_message,
    verify_message,
    canonical_trace_hash,
    sign_trace_dict,
    verify_trace_dict,
)


def test_ed25519_basic_sign_verify():
    """Verify Ed25519 signature algorithm correctness."""
    priv, pub = generate_keypair()
    msg = b"INFINI portable agent workflow specification"
    sig = sign_message(priv, msg)
    assert len(sig) == 64
    assert verify_message(pub, msg, sig) is True
    assert verify_message(pub, b"corrupted message", sig) is False


def test_trace_signing_and_verification():
    """Assert that sign_trace_dict produces an authenticatable trace payload."""
    trace = {
        "loopfile": "test-loop",
        "loopfile_hash": "sha256:abc123",
        "engine": {"type": "infini-reference"},
        "outcome": "verified",
        "steps": [
            {"id": "s1", "name": "step1", "status": "ok", "cost": {"dollars": 0.01}}
        ],
        "verifications": [{"check": "file:exists", "status": "pass"}],
        "provenance": {},
    }

    priv, pub = generate_keypair(b"deterministic-test-seed-1234567890123456")
    signed_trace, sig_hex, pub_hex = sign_trace_dict(trace, secret_key=priv)

    assert "engine_signature" in signed_trace["provenance"]
    assert signed_trace["provenance"]["engine_signature"].startswith("ed25519:")
    assert signed_trace["provenance"]["public_key"] == f"ed25519:{pub_hex}"

    # Verify signature
    valid, reason = verify_trace_dict(signed_trace)
    assert valid is True
    assert "Valid Ed25519 signature" in reason

    # Verify with explicit public key argument
    valid_pub, _ = verify_trace_dict(signed_trace, expected_pubkey_hex=pub_hex)
    assert valid_pub is True


def test_tampered_trace_rejection():
    """Assert that any modification to a signed trace invalidates verification."""
    trace = {
        "loopfile": "test-loop",
        "outcome": "verified",
        "steps": [{"id": "s1", "status": "ok"}],
        "provenance": {},
    }
    priv, pub = generate_keypair()
    signed_trace, _, _ = sign_trace_dict(trace, secret_key=priv)

    # Tamper with outcome
    tampered_trace = json.loads(json.dumps(signed_trace))
    tampered_trace["outcome"] = "unverified"
    valid, reason = verify_trace_dict(tampered_trace)
    assert valid is False
    assert "Signature verification failed" in reason

    # Tamper with steps
    tampered_steps = json.loads(json.dumps(signed_trace))
    tampered_steps["steps"][0]["status"] = "failed"
    valid_step, reason_step = verify_trace_dict(tampered_steps)
    assert valid_step is False
    assert "Signature verification failed" in reason_step

