"""Tests for Agent Pay adapter, budget payment hooks, escrow holds, and settlement receipts."""
import pytest
from infini.parse import parse
from infini.agent_pay import AgentPayAdapter
from infini.engine import run
from infini.trace import new_trace, finalize_trace


PAYMENT_LOOPFILE_YAML = """\
LOOPFILE: "1.0"
name: payment-test-loop
version: 1.0.0
OBJECTIVE: "Test agent pay integration."
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS:
  - { id: s1, name: paid_step, action: fetch_paid_data, uses: builder }
VERIFY:
  syntactic: ["out.json:valid"]
  semantic: ["judge:correctness>=80"]
  confidence_threshold: 80
BUDGET:
  dollars: 10
  minutes: 5
  payment_method: http402
  settlement: hold_until_verified
  wallet_address: "0x402_test_wallet_123"
STOP_WHEN: ["all_verify_passed"]
"""


def test_parse_budget_payment_hooks():
    """Loopfile with budget payment hooks parses correctly."""
    lf = parse(PAYMENT_LOOPFILE_YAML)
    assert lf.budget.dollars == 10
    assert lf.budget.payment_method == "http402"
    assert lf.budget.settlement == "hold_until_verified"
    assert lf.budget.wallet_address == "0x402_test_wallet_123"


def test_agent_pay_escrow_and_settle():
    """AgentPayAdapter holds funds in escrow and releases them upon verification."""
    lf = parse(PAYMENT_LOOPFILE_YAML)
    adapter = AgentPayAdapter()

    # Place hold
    hold = adapter.hold_in_escrow(lf, step_id="s1", amount_usd=1.50)
    assert hold.status == "held"
    assert hold.amount_usd == 1.50
    assert hold.payment_method == "http402"

    # Simulate verified trace
    trace = new_trace(lf.name, PAYMENT_LOOPFILE_YAML)
    finalize_trace(trace, outcome="verified")

    settlement = adapter.settle_or_refund(trace, lf)
    assert settlement["status"] == "settled"
    assert settlement["settled_amount_usd"] == 1.50
    assert settlement["payment_method"] == "http402"
    assert settlement["receipt_hash"].startswith("sha256:")
    assert trace.settlement["status"] == "settled"


def test_agent_pay_escrow_refund_on_failure():
    """Escrow funds are refunded if execution outcome is unverified."""
    lf = parse(PAYMENT_LOOPFILE_YAML)
    adapter = AgentPayAdapter()

    adapter.hold_in_escrow(lf, step_id="s1", amount_usd=2.00)

    # Simulate unverified trace
    trace = new_trace(lf.name, PAYMENT_LOOPFILE_YAML)
    finalize_trace(trace, outcome="unverified")

    settlement = adapter.settle_or_refund(trace, lf)
    assert settlement["status"] == "refunded"
    assert settlement["refunded_amount_usd"] == 2.00
    assert trace.settlement["status"] == "refunded"


def test_agent_pay_budget_exceeded_hold():
    """Holding more than budget throws ValueError."""
    lf = parse(PAYMENT_LOOPFILE_YAML)
    adapter = AgentPayAdapter()

    with pytest.raises(ValueError, match="exceeds declared BUDGET limit"):
        adapter.hold_in_escrow(lf, step_id="s1", amount_usd=15.00)


def test_engine_end_to_end_with_agent_pay(tmp_path):
    """Reference engine run executes with payment hooks and emits settlement receipt."""
    lf = parse(PAYMENT_LOOPFILE_YAML)
    trace = run(lf, output_dir=tmp_path, mock=True, deterministic=True, verbose=False)

    assert trace.outcome == "verified"
    assert trace.settlement is not None
    assert trace.settlement["status"] == "settled"
    assert trace.settlement["payment_method"] == "http402"
    assert trace.settlement["receipt_hash"].startswith("sha256:")
