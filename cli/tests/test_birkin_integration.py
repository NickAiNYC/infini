"""Tests for decoupled governance hooks and Birkin pre-action authorization."""
from __future__ import annotations

import pytest
from infini.governance import MockGovernanceHook, GovernanceDecision
from infini.parse import parse
from infini.engine import run


def test_mock_governance_hook_allows_standard_action():
    hook = MockGovernanceHook()
    decision = hook.evaluate(step_id="s1", action="fs.write", args={"path": "/tmp/out.txt"})
    assert decision.allowed is True
    assert decision.receipt_id == "rcpt_s1_ok"


def test_mock_governance_hook_blocks_shell_action():
    hook = MockGovernanceHook()
    decision = hook.evaluate(step_id="s2", action="shell.exec", args={"cmd": "rm -rf /"})
    assert decision.allowed is False
    assert decision.rule == "shell.deny"


def test_birkin_gateway_integration_if_installed():
    """If Birkin is installed in the environment, verify pre-action authorization works."""
    try:
        from birkin.adapters.infini_gateway import InfiniActionGateway
    except ImportError:
        pytest.skip("Birkin is not installed in the local environment")

    gateway = InfiniActionGateway()
    gateway.initialize_workflow("governed-loop", agent_id="infini-runner")

    # Allowed action
    allowed_dec = gateway.evaluate_step(
        tool="fs.write",
        args={"path": "/tmp/birkin/test.txt", "data": "data"},
        justification="Write test data",
    )
    assert allowed_dec.allowed is True
    assert allowed_dec.decision == "allow"
    assert allowed_dec.receipt.verify(gateway.signing_key.public_b64)

    # Denied action
    denied_dec = gateway.evaluate_step(
        tool="shell.exec",
        args={"cmd": "reboot"},
        justification="Reboot host",
    )
    assert denied_dec.allowed is False
    assert denied_dec.decision == "deny"
    assert denied_dec.rule == "shell.exec.deny"
