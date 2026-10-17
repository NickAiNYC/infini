#!/usr/bin/env python3
"""Example MCP server: a tiny notes store.

A real Model Context Protocol server speaking JSON-RPC 2.0 over
stdio (newline-delimited), implemented with the standard library
only. It exists so the INFINI MCP Tool Runtime example and tests
have a genuine server to talk to — no mocks, no network.

Tools:
    write_note {name, content}  → store a note, returns its size
    read_note  {name}           → return a note's content

Run it directly to check it starts (it waits on stdin):
    python3 notes_server.py
"""
from __future__ import annotations

import json
import sys

_NOTES: dict[str, str] = {}

TOOLS = [
    {
        "name": "write_note",
        "description": "Store a note under a name, replacing any existing note.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Note name"},
                "content": {"type": "string", "description": "Note body"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "read_note",
        "description": "Read back a note stored with write_note.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Note name"},
            },
            "required": ["name"],
        },
    },
]


def _text_result(text: str, is_error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def handle(method: str, params: dict) -> dict | None:
    """Return a JSON-RPC result payload, or None for notifications."""
    if method == "initialize":
        return {
            "protocolVersion": params.get("protocolVersion", "2025-03-26"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "infini-example-notes", "version": "1.0.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "write_note":
            _NOTES[args["name"]] = args["content"]
            return _text_result(json.dumps(
                {"name": args["name"], "bytes": len(args["content"])}
            ))
        if name == "read_note":
            if args["name"] not in _NOTES:
                return _text_result(f"note not found: {args['name']}", is_error=True)
            return _text_result(_NOTES[args["name"]])
        return _text_result(f"unknown tool: {name}", is_error=True)
    return None  # unknown methods/notifications: stay silent


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
            continue  # notification — no response
        result = handle(msg.get("method", ""), msg.get("params") or {})
        if result is None:
            response = {
                "jsonrpc": "2.0", "id": msg["id"],
                "error": {"code": -32601, "message": f"method not found: {msg.get('method')}"},
            }
        else:
            response = {"jsonrpc": "2.0", "id": msg["id"], "result": result}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
