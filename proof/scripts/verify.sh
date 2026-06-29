#!/usr/bin/env bash
# Objective portability check across the two real runs. Exits 1 if broken.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$HERE/runtimes/verify.py" "$HERE/runs/reference/run.json" "$HERE/runs/langgraph/run.json"
