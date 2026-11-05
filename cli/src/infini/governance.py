"""
infini.governance
=================

Lightweight pre-action governance hooks for workflow orchestration.

Provides a decoupled interface allowing external policy and authorization
engines (such as Birkin) to evaluate and sign step authorizations prior to
execution, without hard-coding runtime dependencies.
"""
from __future__ import annotations

from typing import Any, Optional


class GovernanceDecision:
    def __init__(
        self,
        allowed: bool,
        provider: str = "mock",
        receipt_id: str | None = None,
        rule: str | None = None,
        reason: str | None = None,
        receipt: Any = None,
    ):
        self.allowed = allowed
        self.provider = provider
        self.receipt_id = receipt_id
        self.rule = rule
        self.reason = reason
        self.receipt = receipt

    def to_dict(self) -> dict[str, Any]:
        d = {
            "allowed": self.allowed,
            "provider": self.provider,
            "receipt_id": self.receipt_id,
            "rule": self.rule,
            "reason": self.reason,
        }
        if self.receipt is not None:
            d["receipt"] = getattr(self.receipt, "model_dump", lambda: str(self.receipt))()
        return d


class BaseGovernanceHook:
    def evaluate(self, step_id: str, action: str, args: dict[str, Any]) -> GovernanceDecision:
        raise NotImplementedError


class MockGovernanceHook(BaseGovernanceHook):
    """Default fail-closed mock governance hook."""

    def evaluate(self, step_id: str, action: str, args: dict[str, Any]) -> GovernanceDecision:
        if action.startswith("shell") or "rm -rf" in str(args):
            return GovernanceDecision(
                allowed=False,
                provider="mock-policy",
                rule="shell.deny",
                reason="Shell execution blocked by default safety policy",
            )
        return GovernanceDecision(
            allowed=True,
            provider="mock-policy",
            receipt_id=f"rcpt_{step_id}_ok",
            rule="tool.allow",
            reason="Tool invocation permitted",
        )
