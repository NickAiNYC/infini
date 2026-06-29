"""Run A — INFINI reference runtime.

Parses the Loopfile with INFINI's real parser/validator, walks the STEPS DAG in
dependency order, executes each step's deterministic action (writing real
artifacts), runs objective verification, and emits a trace.

No mock. No RNG. Every artifact and every hash is computed from real bytes.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PROOF = Path(__file__).resolve().parent.parent
REPO = PROOF.parent
sys.path.insert(0, str(REPO / "cli" / "src"))     # INFINI's real parser
sys.path.insert(0, str(PROOF))                      # proof_lib

from infini.parse import parse_file                 # noqa: E402  (genuine INFINI code)
from proof_lib import steps, verify_lib, trace_util  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _toposort(loopfile) -> list[str]:
    """Kahn's algorithm: a dependency-respecting order, ties broken by step id."""
    deps = {s.id: set(s.depends_on) for s in loopfile.steps}
    ready = sorted([sid for sid, d in deps.items() if not d])
    order: list[str] = []
    while ready:
        nxt = ready.pop(0)
        order.append(nxt)
        for sid, d in deps.items():
            if nxt in d:
                d.discard(nxt)
                if not d and sid not in order and sid not in ready:
                    ready.append(sid)
        ready.sort()
    return order


def run(work: Path) -> dict:
    loopfile = parse_file(PROOF / "Loopfile.yaml")
    by_id = {s.id: s for s in loopfile.steps}
    started = _now()

    executed_order: list[str] = []
    step_records: list[dict] = []

    for sid in _toposort(loopfile):
        step = by_id[sid]
        if step.action == "verify":
            continue  # verification is a post-execution phase, not an artifact node
        artifacts = steps.execute_action(step.action, work)
        step_records.append({
            "id": step.id, "name": step.name, "agent": step.uses, "action": step.action,
            "status": "ok",
            "artifacts": [{"path": a, "sha256": trace_util.sha256_path(work / a)} for a in artifacts],
        })
        executed_order.append(sid)

    verifications, all_passed = verify_lib.run_verification(
        loopfile.verify.syntactic + loopfile.verify.semantic, work
    )
    outcome = "verified" if all_passed else "unverified"
    ended = _now()

    return trace_util.build_trace(
        loopfile=loopfile,
        engine={"type": "infini-reference", "version": "1.0.0", "orchestrator": "kahn-dag-walk"},
        executed_order=executed_order,
        step_records=step_records,
        verifications=verifications,
        outcome=outcome,
        started_at=started, ended_at=ended,
    )


def main() -> int:
    work = Path(sys.argv[1]) if len(sys.argv) > 1 else (PROOF / "runs" / "reference")
    work.mkdir(parents=True, exist_ok=True)
    # link fixtures into the working dir so steps can read them
    fx = work / "fixtures"
    fx.mkdir(exist_ok=True)
    (fx / "commits.json").write_text((PROOF / "fixtures" / "commits.json").read_text())

    trace = run(work)
    import json
    (work / "run.json").write_text(json.dumps(trace, indent=2) + "\n")
    print(f"[reference] outcome={trace['outcome']} "
          f"order={trace['executed_order']} "
          f"artifacts={sum(len(s['artifacts']) for s in trace['steps'])}")
    return 0 if trace["outcome"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
