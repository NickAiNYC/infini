#!/usr/bin/env bash
# INFINI 60-Second Reproducible Demonstration
# Proves: portable workflow execution, trace generation, time-travel replay, and cross-engine trace diffing.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  INFINI — 60-Second Reproducible Demonstration"
echo "  Portable AI Agent Workflow Infrastructure"
echo "============================================================"
echo ""

# Helper to validate that a specific python binary meets the minimum version requirement (>= 3.11)
check_python_version() {
  local py="$1"
  "$py" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null
}

# 1. Environment & Python discovery (guarantees local repository execution and validates interpreter version)
PYTHON_EXEC=""
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ] && check_python_version "${VIRTUAL_ENV}/bin/python"; then
  PYTHON_EXEC="${VIRTUAL_ENV}/bin/python"
elif [ -d "venv" ] && [ -x "venv/bin/python" ] && check_python_version "venv/bin/python"; then
  PYTHON_EXEC="venv/bin/python"
elif [ -d ".venv" ] && [ -x ".venv/bin/python" ] && check_python_version ".venv/bin/python"; then
  PYTHON_EXEC=".venv/bin/python"
else
  # Discover compatible Python runtime (>= 3.11)
  for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if check_python_version "$candidate"; then
        PYTHON_EXEC="$candidate"
        break
      fi
    fi
  done

  if [ -z "$PYTHON_EXEC" ]; then
    echo "ERROR: INFINI requires Python >= 3.11, but none was found in PATH." >&2
    exit 1
  fi

  echo "Setting up repository virtual environment (.venv) using $PYTHON_EXEC..."
  "$PYTHON_EXEC" -m venv .venv
  PYTHON_EXEC=".venv/bin/python"
  "$PYTHON_EXEC" -m pip install --upgrade pip -q
  "$PYTHON_EXEC" -m pip install -q -e .
fi

# Ensure infini package is imported from this repository
export PYTHONPATH="${SCRIPT_DIR}/cli/src:${PYTHONPATH:-}"

run_infini() {
  "$PYTHON_EXEC" -m infini.cli "$@"
}

# 2. Isolated temporary workspace for demonstration run artifacts
DEMO_RUNS_DIR="$(mktemp -d "${TMPDIR:-/tmp}/infini-demo-XXXXXX")"
trap 'rm -rf "${DEMO_RUNS_DIR}"' EXIT

REF_RUN="${DEMO_RUNS_DIR}/ref"
REPLAY_RUN="${DEMO_RUNS_DIR}/replay-s1"
LANGGRAPH_RUN="${DEMO_RUNS_DIR}/langgraph"

echo "1. Executing workflow on reference engine (zero credentials required)..."
run_infini run examples/quickstart.yaml -o "$REF_RUN" -q
echo "   ✓ Completed. Trace recorded to $REF_RUN/run.json"
echo ""

echo "2. Inspecting structured execution trace..."
run_infini inspect "$REF_RUN"
echo ""

echo "3. Deterministic time-travel replay from step 's1'..."
run_infini replay "$REF_RUN" --step s1 -o "$REPLAY_RUN"
echo ""

echo "4. Executing same Loopfile on simulated LangGraph adapter (experimental/mock)..."
run_infini run examples/quickstart.yaml --engine langgraph -o "$LANGGRAPH_RUN" -q
DIFF_OUTPUT="$(run_infini diff "$REF_RUN/run.json" "$LANGGRAPH_RUN/run.json")"
echo "$DIFF_OUTPUT"
echo ""

# 5. Assertions on trace structure, artifacts, and divergence
echo "5. Validating demonstration artifacts, replay determinism, and trace integrity..."

# Check existence and non-empty status of all traces
for trace_path in "$REF_RUN/run.json" "$REPLAY_RUN/run.json" "$LANGGRAPH_RUN/run.json"; do
  if [ ! -s "$trace_path" ]; then
    echo "ERROR: Expected demonstration trace was not generated: $trace_path" >&2
    exit 1
  fi
done

# Perform deep verification of trace contents and expected behavior
"$PYTHON_EXEC" - <<EOF
import json, sys

with open("$REF_RUN/run.json") as f:
    ref = json.load(f)
assert ref.get("outcome") == "verified", f"Ref outcome {ref.get('outcome')} != verified"
assert ref.get("engine", {}).get("type") == "infini-reference", "Unexpected ref engine type"
steps = ref.get("steps", [])
assert len(steps) >= 1, "Ref steps empty"
artifacts = steps[0].get("artifacts", [])
assert "report.md" in artifacts, f"Expected artifact 'report.md' missing from ref trace: {artifacts}"

with open("$REPLAY_RUN/run.json") as f:
    rep = json.load(f)
assert rep.get("outcome") == "verified", f"Replay outcome {rep.get('outcome')} != verified"
assert rep.get("replay_from_step") == "s1", "Replay did not record replay_from_step == s1"
rep_steps = rep.get("steps", [])
assert len(rep_steps) >= 1, "Replay steps empty"
rep_artifacts = rep_steps[0].get("artifacts", [])
assert "report.md" in rep_artifacts, f"Expected artifact 'report.md' missing from replay trace: {rep_artifacts}"

with open("$LANGGRAPH_RUN/run.json") as f:
    lg = json.load(f)
assert lg.get("outcome") == "verified", f"LangGraph outcome {lg.get('outcome')} != verified"
assert lg.get("engine", {}).get("type") == "langgraph", "Unexpected LangGraph engine type"
EOF

# Assert diff output identified first-step divergence
if ! echo "$DIFF_OUTPUT" | grep -q "First Step Divergence"; then
  echo "ERROR: infini diff did not detect expected first-step divergence" >&2
  exit 1
fi

echo "   ✓ Reference trace verified: outcome=verified, produced report.md."
echo "   ✓ Replay trace verified: replayed from step s1, produced report.md."
echo "   ✓ LangGraph trace verified: simulated engine executed and diff isolated divergence."
echo ""

echo "============================================================"
echo "  ✓ Demonstration Complete"
echo "  Workflow executed. Traces generated. Replay and comparison completed."
echo "============================================================"
