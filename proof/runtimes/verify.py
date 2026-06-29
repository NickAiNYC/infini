"""verify.py — the judge. Objective, reproducible, fails loudly.

Compares the reference run and the LangGraph run and asserts the portability
claim on the ESSENTIAL projection only:

  1. both traces are well-formed and each run independently reached `verified`
  2. the declared workflow graph is identical
  3. each run's executed order is a valid topological order of that graph
  4. every produced artifact has an identical content hash across runtimes
  5. verification check outcomes are identical
  6. final outcome is identical

If any essential assertion fails -> prints the exact reason and exits 1.
Differences in timing / engine metadata / fan-out sibling order are reported as
EXPECTED and do not fail the proof.

Usage: verify.py <reference_run.json> <langgraph_run.json>
"""
from __future__ import annotations

import sys
from pathlib import Path

PROOF = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROOF))
from proof_lib import trace_util  # noqa: E402

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def _ok(msg): print(f"{GREEN}  PASS{RESET}  {msg}")
def _no(msg): print(f"{RED}  FAIL{RESET}  {msg}")
def _info(msg): print(f"{DIM}  ~~~~  {msg}{RESET}")


def main() -> int:
    ref_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROOF / "runs/reference/run.json"
    lg_path = Path(sys.argv[2]) if len(sys.argv) > 2 else PROOF / "runs/langgraph/run.json"

    if not ref_path.exists() or not lg_path.exists():
        _no(f"missing trace(s): {ref_path.exists()=} {lg_path.exists()=}")
        return 1

    ref, lg = trace_util.load(ref_path), trace_util.load(lg_path)
    ref_e = trace_util.essential_projection(ref)
    lg_e = trace_util.essential_projection(lg)

    failures: list[str] = []
    print("INFINI portability proof — objective verification\n")

    # 1. each run independently verified
    if ref["outcome"] == "verified":
        _ok("reference run reached outcome=verified")
    else:
        failures.append(f"reference outcome={ref['outcome']}"); _no(f"reference outcome={ref['outcome']}")
    if lg["outcome"] == "verified":
        _ok("langgraph run reached outcome=verified")
    else:
        failures.append(f"langgraph outcome={lg['outcome']}"); _no(f"langgraph outcome={lg['outcome']}")

    # 2. identical declared workflow graph
    if ref_e["workflow_graph"] == lg_e["workflow_graph"]:
        _ok(f"workflow graph identical ({len(ref_e['workflow_graph'])} steps)")
    else:
        failures.append("workflow graph differs"); _no("workflow graph differs between runtimes")

    # 3. executed order is a valid topological order of the execution DAG
    exec_graph = [g for g in ref_e["workflow_graph"] if g["action"] != "verify"]
    for label, tr in (("reference", ref), ("langgraph", lg)):
        ok, why = trace_util.is_topological(tr["executed_order"], exec_graph)
        if ok:
            _ok(f"{label} executed_order {tr['executed_order']} respects all dependencies")
        else:
            failures.append(f"{label} order invalid: {why}"); _no(f"{label} order invalid: {why}")

    # 4. identical artifact content hashes (the strong claim)
    if ref_e["artifacts"] == lg_e["artifacts"]:
        for path, h in ref_e["artifacts"].items():
            _ok(f"artifact identical  {path}  {h[:19]}…")
    else:
        all_paths = sorted(set(ref_e["artifacts"]) | set(lg_e["artifacts"]))
        for p in all_paths:
            r, l = ref_e["artifacts"].get(p), lg_e["artifacts"].get(p)
            if r != l:
                failures.append(f"artifact mismatch {p}")
                _no(f"artifact MISMATCH  {p}\n          ref={r}\n          lg ={l}")

    # 5. identical verification outcomes
    if ref_e["verifications"] == lg_e["verifications"]:
        npass = sum(1 for v in ref_e["verifications"] if v["status"] == "pass")
        _ok(f"verification outcomes identical ({npass}/{len(ref_e['verifications'])} checks pass)")
    else:
        failures.append("verification outcomes differ"); _no("verification outcomes differ between runtimes")

    # 6. identical final outcome
    if ref_e["outcome"] == lg_e["outcome"]:
        _ok(f"final outcome identical: {ref_e['outcome']}")
    else:
        failures.append("final outcome differs"); _no("final outcome differs")

    # Expected, non-essential differences (reported, never failed)
    print()
    _info(f"engine differs (expected): {ref['engine']['type']} vs {lg['engine']['type']}")
    _info(f"timing differs (expected): ref {ref['started_at']} → {ref['ended_at']}")
    _info(f"                           lg  {lg['started_at']} → {lg['ended_at']}")
    if ref["executed_order"] != lg["executed_order"]:
        _info(f"fan-out sibling order differs (expected, both valid): "
              f"{ref['executed_order']} vs {lg['executed_order']}")

    print()
    if failures:
        print(f"{RED}PORTABILITY BROKEN — {len(failures)} essential assertion(s) failed:{RESET}")
        for f in failures:
            print(f"{RED}  • {f}{RESET}")
        return 1
    print(f"{GREEN}PORTABILITY HOLDS — all essential assertions reproduced across both runtimes.{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
