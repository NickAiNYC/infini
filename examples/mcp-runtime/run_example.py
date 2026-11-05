#!/usr/bin/env python3
"""Run the MCP Tool Runtime example end to end — no LLM key needed.

Loads the example Loopfile, starts the MCP server it declares in its
TOOLS block, discovers the server's tools over the real MCP
protocol, filters them to what the agent declared, makes two calls
(write_note, then read_note), and prints the trace-shaped call
records the runtime produces.

    python3 examples/mcp-runtime/run_example.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "cli" / "src"))

from infini.parse import parse_file          # noqa: E402
from infini.mcp_runtime import McpToolRuntime  # noqa: E402


def main() -> int:
    loopfile = parse_file(HERE / "Loopfile.yaml")
    print(f"Loopfile: {loopfile.name} — TOOLS entries: {len(loopfile.tools)}")

    agent = loopfile.agents[0]
    with McpToolRuntime(loopfile.tools, base_dir=HERE) as runtime:
        print("\nServer status:")
        print(json.dumps(runtime.trace_summary(), indent=2))

        defs = runtime.tools_for_agent(agent)
        print(f"\nTools exposed to agent '{agent.name}':")
        for d in defs:
            print(f"  - {d['name']}: {d['description']}")

        print("\nCall records (trace shape):")
        write = runtime.call(
            "notes.write_note",
            {"name": "standup", "content": "MCP runtime example: write, then read."},
        )
        print(json.dumps(write, indent=2, default=str))

        read = runtime.call("notes.read_note", {"name": "standup"})
        print(json.dumps(read, indent=2, default=str))

        missing = runtime.call("notes.read_note", {"name": "does-not-exist"})
        print(json.dumps(missing, indent=2, default=str))

    ok = write["ok"] and read["ok"] and read["result"] == "MCP runtime example: write, then read."
    print(f"\nExample {'PASSED' if ok else 'FAILED'}: server launched, tools "
          f"discovered, write/read round-trip verified, unknown note classified "
          f"as {missing['status']}.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
