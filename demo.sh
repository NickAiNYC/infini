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

# Ensure virtualenv / infini executable in PATH
if [ -d "venv" ]; then
  # shellcheck source=/dev/null
  source venv/bin/activate
elif [ -d ".venv" ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
elif command -v infini >/dev/null 2>&1; then
  : # infini already in PATH
else
  PYTHON_BIN=""
  for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        PYTHON_BIN="$candidate"
        break
      fi
    fi
  done

  if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: INFINI requires Python >= 3.11, but none was found in PATH." >&2
    exit 1
  fi

  echo "Setting up repository virtual environment (.venv) using $PYTHON_BIN..."
  "$PYTHON_BIN" -m venv .venv
  # shellcheck source=/dev/null
  source .venv/bin/activate
  python -m pip install --upgrade pip -q
  pip install -q -e .
fi

echo "1. Executing workflow on reference engine (zero credentials required)..."
infini run examples/quickstart.yaml -o runs/demo-ref/ -q
echo "   ✓ Completed. Trace recorded to runs/demo-ref/run.json"
echo ""

echo "2. Inspecting structured execution trace..."
infini inspect runs/demo-ref/
echo ""

echo "3. Deterministic time-travel replay from step 's1'..."
infini replay runs/demo-ref/ --step s1
echo ""

echo "4. Executing same Loopfile on LangGraph adapter & diffing execution traces..."
infini run examples/quickstart.yaml --engine langgraph -o runs/demo-langgraph/ -q
infini diff runs/demo-ref/run.json runs/demo-langgraph/run.json
echo ""

# Assert expected artifact generation and valid JSON formatting
echo "5. Validating demonstration artifacts and exit integrity..."
for trace_path in "runs/demo-ref/run.json" "runs/replay-s1/run.json" "runs/demo-langgraph/run.json"; do
  if [ ! -s "$trace_path" ]; then
    echo "ERROR: Expected demonstration trace was not generated: $trace_path" >&2
    exit 1
  fi
  python3 -m json.tool "$trace_path" >/dev/null 2>&1 || {
    echo "ERROR: Trace file is not valid JSON: $trace_path" >&2
    exit 1
  }
done
echo "   ✓ All expected trace files verified and valid JSON."
echo ""

echo "============================================================"
echo "  ✓ Demonstration Complete"
echo "  Workflow executed. Traces generated. Replay and comparison completed."
echo "============================================================"

