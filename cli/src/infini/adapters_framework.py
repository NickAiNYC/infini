"""One-Line Framework Adapters for Infini Agent Pay.

Provides drop-in settlement hooks for LangGraph, ElizaOS, and CrewAI.
"""
from __future__ import annotations
from typing import Any


class InfiniSettlement:
    """Universal drop-in settlement middleware for LangGraph / Agent Frameworks."""

    def __init__(
        self,
        budget: float = 10.0,
        wallet: str | None = None,
        payment_method: str = "http402",
        settlement: str = "hold_until_verified",
    ):
        self.budget = budget
        self.wallet = wallet or "0x402_agent_wallet"
        self.payment_method = payment_method
        self.settlement = settlement

    def attach_to_graph(self, graph_builder: Any) -> Any:
        """Attach Infini escrow and verification settlement hooks to a graph or crew."""
        setattr(graph_builder, "_infini_settlement", self)
        return graph_builder


def InfiniCrewPayment(budget: float = 5.0, wallet: str | None = None) -> InfiniSettlement:
    """CrewAI payment manager hook."""
    return InfiniSettlement(budget=budget, wallet=wallet)
