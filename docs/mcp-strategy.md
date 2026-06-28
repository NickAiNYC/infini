# INFINI × MCP Integration Strategy

> **The game-changer.** Native [Model Context Protocol](https://modelcontextprotocol.io) support turns INFINI from a portability standard into a universal execution engine. Any MCP server, one line of YAML, zero integration code.

---

## Why MCP

The [Model Context Protocol](https://modelcontextprotocol.io) (MCP) is the 2025 standard for connecting tools to AI agents. There are thousands of open-source MCP servers — databases, GitHub, filesystems, browsers, Slack, Notion, every API you can name. Each one exposes a standardized interface that any MCP-aware client can call.

If INFINI can ingest any MCP server directly in the Loopfile, every Loopfile instantly gains access to thousands of capabilities. A developer who wants to build an agent that reads from Postgres, writes to GitHub, and searches the web doesn't write integration code — they drop in three MCP references and write the loop logic.

This is the move that makes INFINI the default starting point for any autonomous project. The portability layer (Loopfile) plus the tool layer (MCP) plus the observability layer (Observatory) is a complete stack.

---

## The spec

The `TOOLS` block in a Loopfile declares MCP servers:

```yaml
TOOLS:
  - mcp: "github.com/modelcontextprotocol/servers/src/postgres"
    config:
      connection_string: "${DATABASE_URL}"
  - mcp: "github.com/modelcontextprotocol/servers/src/filesystem"
    config:
      root: "./workspace"
  - mcp: "github.com/modelcontextprotocol/servers/src/github"
    config:
      token: "${GITHUB_TOKEN}"
```

Agents gain access to MCP tools by listing them in their `tools:` array:

```yaml
AGENTS:
  - name: researcher
    role: researcher
    model_tier: sonnet
    tools: [browser, postgres.query, github.search_repos, filesystem.read]
```

The engine resolves the MCP servers at run time, loads them, and exposes their tools to the agents that declared them.

📖 **Spec reference:** [`spec/loopfile-v1.md`](../spec/loopfile-v1.md) §5b

---

## How it works

```text
Loopfile declares:
  TOOLS:
    - mcp: "github.com/.../src/postgres"
    - mcp: "github.com/.../src/github"

Engine at run time:
  1. Resolves each MCP reference (URL, path, or registry)
  2. Loads the MCP server (subprocess, container, or remote)
  3. Discovers the server's tools (postgres.query, postgres.migrate,
     github.create_issue, github.search_repos, ...)
  4. Exposes tools to agents that declared them in `tools:`
  5. Tool calls appear in the trace with full provenance
  6. On loop exit, MCP servers are torn down
```

The engine handles the lifecycle. The Loopfile author only writes the `TOOLS` block.

---

## Addressing modes

MCP references can be:

| Mode | Example | When to use |
| --- | --- | --- |
| **GitHub path** | `github.com/modelcontextprotocol/servers/src/postgres` | Public MCP servers in the official registry |
| **URL** | `https://mcp.example.com/servers/postgres` | Remote MCP servers (SaaS, internal) |
| **Local path** | `./mcp-servers/postgres` | Local development, custom servers |
| **Registry ref** | `infini/mcp/postgres@1.2` | Versioned MCP servers in the INFINI registry (planned) |

All four modes resolve to the same thing: a running MCP server whose tools are available to the loop.

---

## Tool namespacing

MCP tools are namespaced by server name to avoid collisions:

```yaml
# If two MCP servers both expose a "query" tool:
TOOLS:
  - mcp: "github.com/.../src/postgres"
  - mcp: "github.com/.../src/redis"

# Agents reference them by namespaced name:
AGENTS:
  - name: db_agent
    tools: [postgres.query, redis.query]
```

No ambiguity. No shadowing.

---

## Configuration and secrets

Each MCP entry can carry a `config:` block:

```yaml
TOOLS:
  - mcp: "github.com/.../src/postgres"
    config:
      connection_string: "${DATABASE_URL}"
      max_connections: 10
```

- `${VAR}` syntax references environment variables. The engine substitutes them at run time and never logs the resolved values.
- Config is passed to the MCP server as part of its initialization.
- Config values are **not** included in the trace. Only tool names, arguments, and results are traced.

---

## Budget and rate limiting

MCP servers can declare their own rate limits and costs. The engine respects them:

```yaml
TOOLS:
  - mcp: "github.com/.../src/brave-search"
    config:
      api_key: "${BRAVE_API_KEY}"
      rate_limit: 10           # max 10 calls per second
      cost_per_call: 0.001     # $0.001 per search
```

Tool call costs roll up into the loop's `BUDGET`. If an MCP server's costs push the loop over budget, the engine aborts with `budget_exceeded` — same as any other cost.

---

## Failure handling

If an MCP server is unavailable at run time:

| Failure | Engine behavior |
| --- | --- |
| Server fails to start | Step marked `tool_unavailable`. Loop escalates or retries per `retry:` policy. |
| Server starts but a tool call times out | Step marked `tool_timeout`. Retry if `retry:` is set. |
| Server returns an error | Step marked `tool_error`. Error is captured in the trace. |
| Server exceeds rate limit | Step marked `rate_limited`. Engine backs off and retries. |

All failures are visible in the Observatory, with the MCP server name, the tool called, and the error detail.

---

## Trace integration

Every MCP tool call appears in the trace:

```json
{
  "id": "s2",
  "name": "extract_claims",
  "tools": {
    "calls": [
      {
        "mcp": "github.com/.../src/postgres",
        "tool": "postgres.query",
        "args": { "sql": "SELECT * FROM papers WHERE topic = $1", "params": ["MCP"] },
        "ok": true,
        "rows": 12,
        "duration_ms": 340
      },
      {
        "mcp": "github.com/.../src/github",
        "tool": "github.search_repos",
        "args": { "q": "model context protocol" },
        "ok": true,
        "results": 47,
        "duration_ms": 890
      }
    ]
  }
}
```

The Observatory renders MCP tool calls in the step detail panel, with the server name, the tool, the arguments (redacted of secrets), and the result.

---

## The strategic payoff

| Before MCP | After MCP |
| --- | --- |
| Every tool integration is custom code. | Every tool integration is one line of YAML. |
| Switching tools means rewriting the agent. | Switching tools means changing one `mcp:` reference. |
| Tool calls are invisible in traces. | Tool calls are first-class trace entries. |
| The ecosystem is fragmented per framework. | The ecosystem is unified through MCP. |

A Loopfile with MCP support is the most portable agent artifact possible: declarative logic, declarative tools, declarative verification, declarative budget. Write once. Run anywhere. With any tools.

---

## Roadmap

| Phase | What ships | Status |
| --- | --- | --- |
| **1 — Spec** | `TOOLS` block in Loopfile v1.0. Schema updated. Docs written. | ✅ shipped |
| **2 — Reference engine** | `infini run` loads MCP servers, resolves tools, executes loops. | 🔄 in progress |
| **3 — Observatory** | MCP tool calls rendered in the trace UI. | 🔄 in progress |
| **4 — Registry** | `infini install mcp/postgres@1.2` pulls MCP server configs. | 📋 planned |
| **5 — Marketplace** | Browse MCP-compatible loops by tool capability. | 📋 planned |

---

## Open questions

- **Sandboxing.** Should MCP servers run in subprocesses, containers, or WASM? Current answer: subprocesses for local, containers for untrusted. Open for debate.
- **Authentication.** How do MCP servers authenticate to upstream services? Current answer: `${VAR}` env substitution in `config:`. May add a dedicated `secrets:` block in v1.1.
- **Discovery.** Should the INFINI registry mirror the MCP server registry, or link to it? Current answer: link, don't mirror.
- **Versioning.** MCP servers version independently of INFINI. The `mcp:` reference can pin a version: `github.com/.../src/postgres@1.2`.

---

## See also

- [Loopfile spec §5b — TOOLS (MCP)](../spec/loopfile-v1.md#5b-tools-mcp--model-context-protocol)
- [JSON Schema — `tools` definition](../spec/schema.json)
- [MCP official site](https://modelcontextprotocol.io)
- [MCP servers registry](https://github.com/modelcontextprotocol/servers)

---

## License

CC-BY-4.0. See [repository LICENSE](../LICENSE).
