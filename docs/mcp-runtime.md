# MCP Tool Runtime

The runtime that makes the Loopfile `TOOLS` block real. Before this
change, `TOOLS` (spec [§5b](../spec/loopfile-v1.md)) was schema-only:
Loopfiles could declare MCP servers, but nothing resolved, launched,
or called them. The module previously named `mcp_runtime` was an
in-process registry of built-in tools with placeholder browser
functions — no MCP protocol anywhere.

This is Phase 2 of the [MCP roadmap](handbook/mcp-roadmap.md):
*the reference engine loads MCP servers, resolves tools, executes.*

## What shipped

| Piece | File |
| --- | --- |
| MCP client (JSON-RPC 2.0 over stdio, stdlib only) | `cli/src/infini/mcp_client.py` |
| Runtime: ref resolution, lifecycle, namespacing, call routing, failure classification | `cli/src/infini/mcp_runtime.py` (new layer; the built-in registry above it is unchanged) |
| `Loopfile.tools` parsed from the `TOOLS` block (+ `to_dict` round-trip) | `cli/src/infini/parse.py` |
| Live engine wiring: servers start with the run, discovered tools are offered to the LLM next to built-ins, namespaced calls route to their server, servers are torn down at run end | `cli/src/infini/live_engine.py` |
| Deterministic engine: records declared servers in `trace.extensions["mcp"]` (never launches; conformance stays deterministic) | `cli/src/infini/engine.py` |
| Example: real stdlib MCP server + Loopfile + runnable demo | `examples/mcp-runtime/` |
| Tests: protocol round-trip against a real spawned server, classification, config/env, parse | `cli/tests/test_mcp_runtime.py` |
| Conformance loop exercising a `TOOLS` Loopfile | `tests/conformance/mcp-loop/` |

## Lifecycle (per the strategy doc)

1. **Resolve** each `TOOLS` entry to a launchable server (below).
2. **Load**: spawn the server, run the MCP `initialize` handshake.
3. **Discover**: `tools/list`; namespace every tool as `server.tool`.
4. **Expose**: an agent sees exactly the namespaced tools it listed
   in its `tools:` array (`McpToolRuntime.tools_for_agent`).
5. **Call**: `tools/call` routed to the owning server; the result is
   returned as a trace-shaped record.
6. **Teardown**: on loop exit every server process is shut down.

## Addressing modes — honest scope

| Mode | Example | Resolution |
| --- | --- | --- |
| Local path | `./mcp-servers/postgres`, `./notes_server.py` | Launched directly: a `.py` file runs under the current interpreter; a directory resolves to its `server.py` / `main.py` / `__main__.py`. |
| GitHub path | `github.com/modelcontextprotocol/servers/src/postgres` | Resolved **only** when `config.command` says how to launch it locally. Otherwise the server is reported `unavailable` with that reason — never silently skipped. |
| URL | `https://mcp.example.com/servers/postgres` | Same rule as GitHub: needs `config.command`. A remote HTTP transport is future work. |
| Registry ref | `infini/mcp/postgres@1.2` | Same rule: needs `config.command` until the registry ships (roadmap Phase 4). |

Stdio is the transport because it is how local MCP servers actually
run, and it keeps the CLI dependency-free.

## Config

The per-server `config:` block supports:

- `name` — namespace override (default: last path segment of the ref).
- `command` — explicit launch command (list, or string split shell-style).
- `env` — extra environment for the server process.
- `cwd` — working directory (default: the Loopfile's directory).
- `timeout_seconds` — per-request timeout (default 30).
- `rate_limit` — max calls per second; the runtime throttles.
- `cost_per_call` — rolled into the call record and
  `runtime.total_cost` so loop budgets can account for tool spend.

`${VAR}` references anywhere in config are expanded from the
environment at launch. An unset variable marks the server
unavailable and names the variable. **Resolved values are never
logged, traced, or included in summaries.**

## Failure taxonomy

Matches [docs/mcp-strategy.md](mcp-strategy.md) exactly. One bad
server never sinks the loop: it is marked, and steps depending on it
see the classification in the call record.

| Situation | Record `status` |
| --- | --- |
| Server cannot start / dies / unresolvable ref | `tool_unavailable` |
| Call exceeds the timeout | `tool_timeout` |
| Server answers with a JSON-RPC error or `isError` result | `tool_error` |
| Success | `ok` |

## Trace records

Every call returns (and the live engine appends) the strategy doc's
shape:

```json
{
  "mcp": "github.com/.../src/postgres",
  "tool": "postgres.query",
  "ok": true,
  "status": "ok",
  "result": {"rows": 12},
  "duration_ms": 340,
  "cost": 0.001
}
```

At run start the trace carries `extensions.mcp.servers[]` with each
server's ref, name, mode, status, and discovered tool names —
config values are never included.

## Try it

```bash
python3 examples/mcp-runtime/run_example.py   # no LLM key needed
python3 -m pytest cli/tests/test_mcp_runtime.py
infini conformance tests/conformance
```
