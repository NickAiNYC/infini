#!/usr/bin/env python3
"""Check that spec/schema.json and cli/src/infini/schema.json are in sync.

Exits 0 if they match, 1 if they differ.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SPEC_SCHEMA = REPO_ROOT / "spec" / "schema.json"
CLI_SCHEMA = REPO_ROOT / "cli" / "src" / "infini" / "schema.json"


def main() -> int:
    if not SPEC_SCHEMA.exists():
        print(f"ERROR: spec schema not found: {SPEC_SCHEMA}", file=sys.stderr)
        return 1
    if not CLI_SCHEMA.exists():
        print(f"ERROR: CLI schema not found: {CLI_SCHEMA}", file=sys.stderr)
        return 1

    spec = json.loads(SPEC_SCHEMA.read_text())
    cli = json.loads(CLI_SCHEMA.read_text())

    spec_props = set(spec.get("properties", {}).keys())
    cli_props = set(cli.get("properties", {}).keys())

    if spec_props != cli_props:
        only_in_spec = spec_props - cli_props
        only_in_cli = cli_props - spec_props
        print("ERROR: schema drift detected", file=sys.stderr)
        if only_in_spec:
            print(f"  In spec but not in CLI: {only_in_spec}", file=sys.stderr)
        if only_in_cli:
            print(f"  In CLI but not in spec: {only_in_cli}", file=sys.stderr)
        print(f"\nFix: cp spec/schema.json cli/src/infini/schema.json", file=sys.stderr)
        return 1

    # Check $defs match too
    spec_defs = set(spec.get("$defs", {}).keys())
    cli_defs = set(cli.get("$defs", {}).keys())
    if spec_defs != cli_defs:
        print("ERROR: $defs drift detected", file=sys.stderr)
        print(f"  In spec but not in CLI: {spec_defs - cli_defs}", file=sys.stderr)
        print(f"  In CLI but not in spec: {cli_defs - spec_defs}", file=sys.stderr)
        return 1

    print("OK: spec/schema.json and cli/src/infini/schema.json are in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
