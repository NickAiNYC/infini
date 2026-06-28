# MCP Roadmap

Native Model Context Protocol support — the game-changer that turns
INFINI from a portability standard into a universal execution engine.

> Any MCP server, one line of YAML, zero integration code.

## The spec

```yaml
TOOLS:
  - mcp: "github.com/modelcontextprotocol/servers/src/postgres"
  - mcp: "github.com/modelcontextprotocol/servers/src/github"
  - mcp: "github.com/modelcontextprotocol/servers/src/filesystem"
```

📖 **Full spec:** [`spec/loopfile-v1.md` §5b](../../spec/loopfile-v1.md)
📖 **Integration strategy:** [`docs/mcp-strategy.md`](../mcp-strategy.md)

## Roadmap

| Phase | What ships | Status |
| --- | --- | --- |
| 1 — Spec | `TOOLS` block in schema + docs | ✅ shipped |
| 2 — Reference engine | `infini run` loads MCP servers | 🔄 in progress |
| 3 — Observatory | MCP tool calls in trace UI | 🔄 in progress |
| 4 — Registry | `infini install mcp/postgres@1.2` | 📋 planned |
| 5 — Marketplace | Browse MCP-compatible loops | 📋 planned |

## Cross-links

- [Architecture](architecture.md) — where MCP fits
- [Adapter Development](adapter-development.md) — adapters resolve MCP
- [MCP Strategy](../mcp-strategy.md) — the full integration plan
