"""Run B — LangGraph runtime (REAL StateGraph, not a mock).

This builds an actual `langgraph.graph.StateGraph` from the same Loopfile:
  STEPS      -> nodes
  depends_on -> edges
Each node calls the SAME deterministic step function the reference runtime uses.
The graph is compiled and `invoke`d, so LangGraph itself performs the
orchestration and decides execution order. We capture the real order LangGraph
executed in and emit a trace in the same shape as the reference runtime.

If LangGraph is not installed, this exits non-zero with a clear message — the
proof never silently falls back to a simulation.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict

PROOF = Path(__file__).resolve().parent.parent
REPO = PROOF.parent
sys.path.insert(0, str(REPO / "cli" / "src"))
sys.path.insert(0, str(PROOF))

try:
    from langgraph.graph import StateGraph, END
    from importlib.metadata import version as _pkg_version
    LANGGRAPH_VERSION = _pkg_version("langgraph")
except Exception as e:  # pragma: no cover
    sys.stderr.write(
        "FATAL: langgraph is not installed — the proof requires a REAL second "
        f"runtime, not a simulation.\n  pip install langgraph\n  ({e})\n"
    )
    raise SystemExit(2)

from infini.parse import parse_file                  # noqa: E402  (genuine INFINI code)
from proof_lib import steps, verify_lib, trace_util   # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _merge_executed(a: list, b: list) -> list:
    return a + b


class GraphState(TypedDict):
    work: str
    executed: Annotated[list, _merge_executed]   # reducer: concat across parallel branches
    records: Annotated[list, _merge_executed]


def _make_node(step):
    def node(state: GraphState) -> dict:
        work = Path(state["work"])
        artifacts = steps.execute_action(step.action, work)
        rec = {
            "id": step.id, "name": step.name, "agent": step.uses, "action": step.action,
            "status": "ok",
            "artifacts": [{"path": a, "sha256": trace_util.sha256_path(work / a)} for a in artifacts],
        }
        return {"executed": [step.id], "records": [rec]}
    return node


def build_graph(loopfile):
    """Translate the Loopfile into a REAL LangGraph StateGraph."""
    g = StateGraph(GraphState)
    non_verify = [s for s in loopfile.steps if s.action != "verify"]
    for step in non_verify:
        g.add_node(step.id, _make_node(step))

    roots = [s for s in non_verify if not s.depends_on]
    for s in roots:
        g.add_edge("__start__", s.id)

    for step in non_verify:
        # outgoing edges to steps that depend on this one
        children = [c for c in non_verify if step.id in c.depends_on]
        for child in children:
            g.add_edge(step.id, child.id)
        # leaves (nothing depends on them) flow to END
        if not children:
            g.add_edge(step.id, END)
    return g.compile()


def run(work: Path) -> dict:
    loopfile = parse_file(PROOF / "Loopfile.yaml")
    app = build_graph(loopfile)
    started = _now()

    final = app.invoke({"work": str(work), "executed": [], "records": []})

    executed_order = final["executed"]
    # records may arrive in branch order; sort for stable storage but keep the
    # real executed_order separately (that is the portability-relevant fact).
    step_records = sorted(final["records"], key=lambda r: r["id"])

    verifications, all_passed = verify_lib.run_verification(
        loopfile.verify.syntactic + loopfile.verify.semantic, work
    )
    outcome = "verified" if all_passed else "unverified"
    ended = _now()

    return trace_util.build_trace(
        loopfile=loopfile,
        engine={"type": "langgraph", "version": LANGGRAPH_VERSION, "orchestrator": "StateGraph.invoke"},
        executed_order=executed_order,
        step_records=step_records,
        verifications=verifications,
        outcome=outcome,
        started_at=started, ended_at=ended,
    )


def main() -> int:
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else (PROOF / "runs" / "langgraph")
    work.mkdir(parents=True, exist_ok=True)
    fx = work / "fixtures"
    fx.mkdir(exist_ok=True)
    (fx / "commits.json").write_text((PROOF / "fixtures" / "commits.json").read_text())

    trace = run(work)
    import json
    (work / "run.json").write_text(json.dumps(trace, indent=2) + "\n")
    print(f"[langgraph {LANGGRAPH_VERSION}] outcome={trace['outcome']} "
          f"order={trace['executed_order']} "
          f"artifacts={sum(len(s['artifacts']) for s in trace['steps'])}")
    return 0 if trace["outcome"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
