# INFINI × OpenClaw Adapter

> **OpenClaw is the agent/runtime layer.** This adapter lets any Loopfile execute through OpenClaw agents — with browser, GitHub, terminal, and filesystem tools.

INFINI is not another agent framework. INFINI is the **portable loop standard** that sits above runtimes. OpenClaw handles execution; this adapter translates a Loopfile into OpenClaw tool calls.

Use this adapter when you need:

- **tool execution** — browser actions, GitHub edits, terminal commands, filesystem writes
- **browser actions** — navigate, click, scrape, screenshot
- **repo edits** — branch, commit, push, open PR
- **terminal commands** — run tests, build, deploy
- **agent orchestration** — coordinate multi-tool task completion

For governance (policy, memory, escalation, audit), use the [Hermes adapter](../hermes/) instead. For combined governance + execution, see the [hybrid demo](../../examples/hybrid-hermes-openclaw/).

---

## Architecture

```text
Loopfile
  ↓
INFINI Parser + Validator
  ↓
OpenClaw Adapter             ← you are here
  ↓
OpenClaw agents + tools
  ↓
Trace + Verification + Replay
```

The OpenClaw adapter is responsible for translating Loopfile primitives (`AGENTS`, `STEPS`, `VERIFY`) into OpenClaw agent invocations and tool calls. It does not itself enforce governance policy; that's the Hermes adapter's job.

---

## Install

```bash
pip install infini-cli[openclaw]
```

The adapter is bundled with the INFINI CLI but registered only when the `openclaw` extra is installed.

---

## Configure

A Loopfile declares its engine via the `ENGINE` block:

```yaml
ENGINE:
  type: openclaw
  adapter: adapters/openclaw
  tools:
    - browser
    - github
    - terminal
    - file_system
```

| Field      | Values                                          | Meaning |
| ---------- | ----------------------------------------------- | ------- |
| `type`     | `openclaw`                                      | Selects this adapter. |
| `adapter`  | `adapters/openclaw`                             | Adapter module path. |
| `tools`    | list of `browser` \| `github` \| `terminal` \| `file_system` \| `db` \| `deploy` | Tools the OpenClaw agents are allowed to call. The adapter refuses to call a tool not in this list. |

See [`adapter.yaml`](adapter.yaml) for the adapter's own manifest.

---

## Use OpenClaw for

- **tool execution** — call any tool the agent has access to
- **browser actions** — navigate pages, click, scrape, screenshot
- **repo edits** — branch, commit, push, open pull requests
- **terminal commands** — run tests, build, deploy
- **agent orchestration** — coordinate multiple agents and tools
- **task completion** — get the loop's work actually done

---

## Examples

Three Loopfiles ship with this adapter:

| Loopfile | What it demonstrates |
| -------- | -------------------- |
| [`coding-loop.yaml`](examples/coding-loop.yaml) | Implement a feature: edit files, run tests, verify output. |
| [`browser-agent-loop.yaml`](examples/browser-agent-loop.yaml) | Multi-step browser task: navigate, scrape, screenshot, verify. |
| [`research-loop.yaml`](examples/research-loop.yaml) | Multi-source research with browser + terminal, citations required. |

Run any of them:

```bash
infini run adapters/openclaw/examples/coding-loop.yaml
```

---

## Conformance

This adapter implements:

| Capability       | Status |
| ---------------- | :----: |
| Parse Loopfile   |   ✅   |
| Run Loop         |   ✅   |
| Verify           |   ✅   |
| Inspect Trace    |   ✅   |
| Replay           |   🚧   |
| Diff             |   🚧   |

The full conformance row lives in [`spec/compatibility.md`](../../spec/compatibility.md).

---

## Tool execution extensions

The OpenClaw adapter emits tool-call fields in the trace:

```json
{
  "tools": {
    "calls": [
      { "step": "s2", "tool": "file_system.write", "target": "src/auth.py",  "ok": true },
      { "step": "s3", "tool": "terminal.run",      "target": "pytest -q",   "ok": true, "exit": 0 },
      { "step": "s4", "tool": "github.pr",         "target": "feature/auth","ok": true, "pr": 4129 }
    ],
    "denied": []
  }
}
```

These are visible in the Loop Observatory under the **Tools** tab.

---

## License

MIT. See [repository LICENSE](../../LICENSE).
