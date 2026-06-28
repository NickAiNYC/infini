#!/usr/bin/env python3
"""Quick smoke test for the loom CLI against every canonical loop."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
LOOPS = ROOT / "loops"
CLI = ROOT / "cli" / "loom.py"

def main() -> int:
    failures = []
    for f in sorted(LOOPS.glob("*.yaml")):
        result = subprocess.run(
            [sys.executable, str(CLI), "validate", str(f)],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        print(f"{'✓' if ok else '✗'} {f.name}")
        if not ok:
            failures.append(f.name)
            print(result.stderr)

    if failures:
        print(f"\n❌ {len(failures)} loop(s) failed validation: {failures}")
        return 1
    print(f"\n✓ all loops valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
