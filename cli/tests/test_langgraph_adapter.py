"""Test the LangGraph adapter against the conformance suite."""
import pytest
import sys
from pathlib import Path

# Add the adapters directory to path
# test file is at cli/tests/test_langgraph_adapter.py
# adapter is at adapters/langgraph/langgraph_adapter.py
# need to go up 3 levels from cli/tests/ to repo root
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "adapters" / "langgraph"))

from langgraph_adapter import LangGraphAdapter
from infini.parse import parse


VALID_LOOPFILE = """\
LOOPFILE: "1.0"
name: test-langgraph
version: 1.0.0
OBJECTIVE: "Test the LangGraph adapter."
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
  - { name: verifier, role: verifier, model_tier: haiku }
STEPS:
  - { id: s1, name: step1, action: do_thing, uses: builder, produces: [out.txt] }
  - { id: s2, name: step2, action: verify, uses: verifier, depends_on: [s1] }
VERIFY:
  syntactic: ["out.txt:exists"]
  semantic: ["judge:quality>=80"]
  confidence_threshold: 80
BUDGET: { dollars: 5, minutes: 10 }
STOP_WHEN: ["all_verify_passed"]
"""


def test_langgraph_adapter_parses_loopfile():
    """The adapter can parse a Loopfile."""
    adapter = LangGraphAdapter()
    lf = adapter.parse(VALID_LOOPFILE)
    assert lf.name == "test-langgraph"
    assert len(lf.steps) == 2


def test_langgraph_adapter_translates_to_state_graph():
    """The adapter translates steps to nodes and depends_on to edges."""
    adapter = LangGraphAdapter()
    lf = adapter.parse(VALID_LOOPFILE)
    graph = adapter.to_state_graph(lf)

    assert "s1" in graph["nodes"]
    assert "s2" in graph["nodes"]
    assert graph["entry"] == "s1"
    assert len(graph["edges"]) >= 2  # s1→s2 + s2→verify

    # Check edge from s1 to s2 (depends_on)
    dep_edges = [e for e in graph["edges"] if e["from"] == "s1" and e["to"] == "s2"]
    assert len(dep_edges) == 1


def test_langgraph_adapter_run_mock_produces_trace():
    """Running in mock mode produces a valid INFINI trace."""
    adapter = LangGraphAdapter()
    lf = adapter.parse(VALID_LOOPFILE)
    trace = adapter.run(lf, mock=True, output_dir="/tmp/test-lg-run", verbose=False)

    assert trace.outcome == "verified"
    assert trace.engine["type"] == "langgraph"
    assert len(trace.steps) == 2  # s1 + s2
    assert trace.steps[0].id == "s1"
    assert trace.steps[1].id == "s2"
    assert len(trace.verifications) == 2  # 1 syntactic + 1 semantic


def test_langgraph_trace_format_matches_reference():
    """The LangGraph trace has the same structure as the reference engine trace."""
    adapter = LangGraphAdapter()
    lf = adapter.parse(VALID_LOOPFILE)
    trace = adapter.run(lf, mock=True, output_dir="/tmp/test-lg-format", verbose=False)

    # Check trace has all required fields (same as reference engine)
    assert trace.loopfile is not None
    assert trace.loopfile_hash is not None
    assert trace.engine is not None
    assert trace.started_at is not None
    assert trace.ended_at is not None
    assert trace.iterations >= 1
    assert isinstance(trace.steps, list)
    assert isinstance(trace.verifications, list)
    assert isinstance(trace.budget, dict)
    assert "spent_dollars" in trace.budget
    assert "spent_minutes" in trace.budget


def test_langgraph_adapter_budget_enforcement():
    """The adapter enforces BUDGET."""
    adapter = LangGraphAdapter()
    lf = adapter.parse(VALID_LOOPFILE.replace("dollars: 5", "dollars: 0.001"))
    trace = adapter.run(lf, mock=True, output_dir="/tmp/test-lg-budget", verbose=False)
    assert trace.outcome == "budget_exceeded"
