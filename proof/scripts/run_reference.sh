#!/usr/bin/env bash
# Run A — INFINI reference runtime. Produces runs/reference/{run.json,artifacts}.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$HERE/runtimes/run_reference.py" "$HERE/runs/reference"
