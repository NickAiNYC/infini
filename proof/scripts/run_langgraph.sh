#!/usr/bin/env bash
# Run B — REAL LangGraph runtime. Produces runs/langgraph/{run.json,artifacts}.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -c "import langgraph" 2>/dev/null || { echo "FATAL: pip install langgraph"; exit 2; }
python3 "$HERE/runtimes/run_langgraph.py" "$HERE/runs/langgraph"
