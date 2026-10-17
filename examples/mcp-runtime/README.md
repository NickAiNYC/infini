# Example: MCP Tool Runtime

A Loopfile whose tools come from a **real MCP server**, not from
code compiled into the engine.

## What's here

| File | What it is |
| --- | --- |
| `notes_server.py` | A genuine MCP server (JSON-RPC 2.0 over stdio, stdlib only) exposing `write_note` / `read_note`. |
| `Loopfile.yaml` | A Loopfile declaring the server in its `TOOLS` block; the agent lists the namespaced tools `notes.write_note`, `notes.read_note`. |
| `run_example.py` | Drives `McpToolRuntime` end to end with no LLM key: launch, discover, filter per agent, call, classify. |

## Run it

```bash
python3 examples/mcp-runtime/run_example.py
```

You should see the server reported `ready` with its two namespaced
tools, then three trace-shaped call records: a successful write, a
successful read returning the same content, and a read of a missing
note classified as `tool_error`.

## How it maps to the spec

- The `TOOLS` block is [spec §5b](../../spec/loopfile-v1.md#5b-tools-mcp--model-context-protocol).
- Server name `notes` comes from `config.name`; tools are
  namespaced `server.tool` exactly as the spec requires.
- Design and scope notes: [docs/mcp-runtime.md](../../docs/mcp-runtime.md).
