#!/usr/bin/env python3
"""Test fixture: a minimal real MCP server over stdio (stdlib only).

Tools: echo {text}, add {a, b}, fail {} (returns isError), sleep {seconds}.
Used by test_mcp_runtime.py — spawned as a subprocess, spoken to over
the actual MCP protocol. Not a mock.
"""
from __future__ import annotations

import json
import sys
import time

TOOLS = [
    {"name": "echo", "description": "Echo text back.",
     "inputSchema": {"type": "object",
                     "properties": {"text": {"type": "string"}},
                     "required": ["text"]}},
    {"name": "add", "description": "Add two numbers.",
     "inputSchema": {"type": "object",
                     "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                     "required": ["a", "b"]}},
    {"name": "fail", "description": "Always returns an MCP error result.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "sleep", "description": "Sleep for N seconds, then answer.",
     "inputSchema": {"type": "object",
                     "properties": {"seconds": {"type": "number"}},
                     "required": ["seconds"]}},
]


def handle(method: str, params: dict) -> dict | None:
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion", "2025-03-26"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "infini-test-server", "version": "0.1.0"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name == "echo":
            return {"content": [{"type": "text", "text": args["text"]}], "isError": False}
        if name == "add":
            return {"content": [{"type": "text", "text": json.dumps({"sum": args["a"] + args["b"]})}],
                    "isError": False}
        if name == "fail":
            return {"content": [{"type": "text", "text": "deliberate failure"}], "isError": True}
        if name == "sleep":
            time.sleep(float(args["seconds"]))
            return {"content": [{"type": "text", "text": "slept"}], "isError": False}
        return {"content": [{"type": "text", "text": f"unknown tool: {name}"}], "isError": True}
    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" not in msg:
            continue
        result = handle(msg.get("method", ""), msg.get("params") or {})
        if result is None:
            resp = {"jsonrpc": "2.0", "id": msg["id"],
                    "error": {"code": -32601, "message": "method not found"}}
        else:
            resp = {"jsonrpc": "2.0", "id": msg["id"], "result": result}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
