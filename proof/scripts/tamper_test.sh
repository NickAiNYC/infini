#!/usr/bin/env bash
# Credibility check: prove verify.sh actually FAILS when portability is broken.
# Corrupts one langgraph artifact, re-traces its hash, and asserts verify exits 1.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo ">> tampering with runs/langgraph/CHANGELOG.md and rehashing its trace..."
python3 - "$HERE" <<'PY'
import json, hashlib, sys
from pathlib import Path
here = Path(sys.argv[1]); work = here/"runs/langgraph"
(work/"CHANGELOG.md").write_text((work/"CHANGELOG.md").read_text()+"\n<!-- tampered -->\n")
t = json.loads((work/"run.json").read_text())
for st in t["steps"]:
    for a in st.get("artifacts", []):
        if a["path"]=="CHANGELOG.md":
            a["sha256"]="sha256:"+hashlib.sha256((work/"CHANGELOG.md").read_bytes()).hexdigest()
(work/"run.json").write_text(json.dumps(t,indent=2)+"\n")
PY
echo ">> running verify.sh against the tampered run (expect FAIL + exit 1)..."
if python3 "$HERE/runtimes/verify.py" "$HERE/runs/reference/run.json" "$HERE/runs/langgraph/run.json"; then
  echo "TAMPER TEST FAILED: verifier passed a broken run — it cannot be trusted."; exit 1
else
  echo "TAMPER TEST PASSED: verifier correctly rejected the broken run (exit 1)."
fi
