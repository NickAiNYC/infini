"""Trace construction and the 'essential projection' used for portability checks.

A trace records everything. But portability is a claim about a *subset* of the
trace: the workflow graph, the dependency-respecting execution, the artifacts
produced (by content hash), and the verification outcome. Timing, engine
metadata, and fan-out sibling ordering are explicitly NOT part of the claim.

`essential_projection` extracts exactly the fields the portability claim covers,
so `verify.py` can assert equality on those and report the rest as expected
differences.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_path(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def loopfile_graph(loopfile) -> list[dict]:
    """The declared workflow graph: ordered steps with their declared deps."""
    return [
        {"id": s.id, "name": s.name, "action": s.action,
         "agent": s.uses, "depends_on": sorted(s.depends_on)}
        for s in loopfile.steps
    ]


def is_topological(order: list[str], graph: list[dict]) -> tuple[bool, str]:
    """True iff `order` lists every step once and never before its dependencies."""
    ids = [g["id"] for g in graph]
    if sorted(order) != sorted(ids):
        return False, f"order {order} does not cover steps {ids}"
    pos = {sid: i for i, sid in enumerate(order)}
    for g in graph:
        for dep in g["depends_on"]:
            if pos[dep] > pos[g["id"]]:
                return False, f"{g['id']} ran before its dependency {dep}"
    return True, "valid topological order"


def build_trace(*, loopfile, engine: dict, executed_order: list[str],
                step_records: list[dict], verifications: list[dict],
                outcome: str, started_at: str, ended_at: str) -> dict:
    return {
        "loopfile": f"infini/{loopfile.name}@{loopfile.version}",
        "spec": loopfile.spec_version,
        "engine": engine,                       # NON-essential (differs by design)
        "started_at": started_at,               # NON-essential
        "ended_at": ended_at,                    # NON-essential
        "workflow_graph": loopfile_graph(loopfile),   # essential
        "executed_order": executed_order,        # essential (must be topological)
        "steps": step_records,                   # essential: artifacts + hashes
        "verifications": verifications,          # essential
        "outcome": outcome,                      # essential
    }


def essential_projection(trace: dict) -> dict:
    """Extract only the fields the portability claim is about."""
    artifacts = {}
    for st in trace["steps"]:
        for a in st.get("artifacts", []):
            artifacts[a["path"]] = a["sha256"]
    return {
        "workflow_graph": trace["workflow_graph"],
        "artifacts": dict(sorted(artifacts.items())),
        "verifications": [
            {"check": v["check"], "status": v["status"]}
            for v in trace["verifications"]
        ],
        "outcome": trace["outcome"],
    }


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
