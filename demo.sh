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
elif command -v infini >/dev/null 2>&1; then
  : # infini already in PATH
else
  echo "Installing infini locally in virtual environment..."
  python3 -m venv .demo_venv
  # shellcheck source=/dev/null
  source .demo_venv/bin/activate
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

echo "============================================================"
echo "  ✓ Demonstration Complete"
echo "  Same Loopfile. Two Engines. Identical Traces."
echo "============================================================"
