"""Tests for the mock verifier and engine."""
import pytest
from infini.mock import mock_verify, mock_execute


def test_mock_verify_deterministic_passes_all():
    """In deterministic mode, all checks pass on iteration 1."""
    # Semantic check
    passed, conf = mock_verify("judge:quality>=85", "test", 1, 85, deterministic=True)
    assert passed is True
    assert conf == 90  # threshold + 5

    # Syntactic check
    passed, conf = mock_verify("file.txt:exists", "test", 1, 85, deterministic=True)
    assert passed is True
    assert conf is None


def test_mock_verify_deterministic_respects_threshold():
    """Deterministic confidence is threshold + 5, capped at 100."""
    passed, conf = mock_verify("judge:quality>=95", "test", 1, 95, deterministic=True)
    assert passed is True
    assert conf == 100  # 95 + 5 = 100, capped


def test_mock_verify_non_deterministic_can_fail():
    """In non-deterministic mode, iteration 1 semantic checks can fail."""
    # Run many times to exercise the random path
    failures = 0
    for i in range(100):
        passed, _ = mock_verify("judge:quality>=85", f"test-{i}", 1, 85, deterministic=False)
        if not passed:
            failures += 1
    # At least some should fail on iteration 1 (below threshold)
    assert failures > 0


def test_mock_execute_is_deterministic_with_same_inputs():
    """Same inputs → same output (deterministic seed)."""
    r1 = mock_execute("s1", "test", "action", "builder", "sonnet", ["out.txt"], "loop", 1)
    r2 = mock_execute("s1", "test", "action", "builder", "sonnet", ["out.txt"], "loop", 1)
    assert r1.cost_dollars == r2.cost_dollars
    assert r1.tokens_in == r2.tokens_in
    assert r1.tokens_out == r2.tokens_out
    assert r1.artifacts == r2.artifacts


def test_mock_execute_different_step_different_output():
    """Different step ID → different output (different seed)."""
    r1 = mock_execute("s1", "a", "act", "builder", "sonnet", ["x.txt"], "loop", 1)
    r2 = mock_execute("s2", "b", "act", "builder", "sonnet", ["y.txt"], "loop", 1)
    # Costs should differ (different seeds → different random values)
    assert r1.cost_dollars != r2.cost_dollars or r1.tokens_in != r2.tokens_in
