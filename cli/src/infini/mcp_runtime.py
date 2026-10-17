"""MCP runtime — tool definitions and execution.

Attribution: decorator-based tool pattern from FastMCP
(https://github.com/jlowin/fastmcp). Each tool is a Python function
with a decorator that registers it in the tool registry. The live
engine sends these definitions to the LLM; the LLM calls tools;
we execute them and return results.

No FastMCP dependency required — we implement the same pattern inline.
This keeps the CLI lightweight and avoids forcing a dependency.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

# Tool registry — maps tool name → function
_TOOLS: dict[str, dict] = {}


def tool(name: str, description: str = ""):
    """Decorator to register a tool. FastMCP-style.

    Usage:
        @tool("file_system.write", "Write content to a file")
        def write_file(path: str, content: str) -> dict:
            ...
    """
    def decorator(func: Callable) -> Callable:
        _TOOLS[name] = {
            "name": name,
            "description": description,
            "function": func,
            "parameters": _extract_params(func),
        }
        return func
    return decorator


def _extract_params(func: Callable) -> dict:
    """Extract parameter schema from function signature."""
    import inspect
    sig = inspect.signature(func)
    properties = {}
    required = []
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        properties[param_name] = {"type": "string"}
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    return {"type": "object", "properties": properties, "required": required}


def get_tool_definitions() -> list[dict]:
    """Get all registered tool definitions for sending to an LLM."""
    return [
        {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
        for t in _TOOLS.values()
    ]


def execute_tool(name: str, **kwargs) -> dict:
    """Execute a tool by name. Returns result dict."""
    if name not in _TOOLS:
        return {"ok": False, "error": f"Unknown tool: {name}"}
    try:
        result = _TOOLS[name]["function"](**kwargs)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ════════════════════════════════════════════════════════════
# Built-in tools — the INFINI standard tool set
# ════════════════════════════════════════════════════════════

@tool("file_system.write", "Write content to a file")
def fs_write(path: str, content: str) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return {"path": str(p), "bytes": len(content)}


@tool("file_system.read", "Read content from a file")
def fs_read(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"error": "not found"}
    return {"path": str(p), "content": p.read_text()}


@tool("terminal.run", "Run a shell command and return output")
def terminal_run(command: str) -> dict:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=120
    )
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout[:5000],
        "stderr": result.stderr[:5000],
    }


@tool("browser.navigate", "Navigate to a URL and return page content (placeholder)")
def browser_navigate(url: str) -> dict:
    # Real implementation would use playwright or requests
    return {"url": url, "status": "placeholder", "content": "(browser not implemented in live mode)"}


@tool("browser.scrape", "Scrape content from the current page (placeholder)")
def browser_scrape(selector: str = "body") -> dict:
    return {"selector": selector, "content": "(browser not implemented in live mode)"}


@tool("memory.recall", "Search past lessons from eternal memory")
def memory_recall(query: str) -> dict:
    from .memory import search_lessons
    results = search_lessons(query, limit=5)
    return {"lessons": [r["content"][:200] for r in results]}


@tool("memory.append", "Store a lesson in eternal memory")
def memory_append(content: str) -> dict:
    from .memory import store_lesson
    lesson_id = store_lesson(content)
    return {"lesson_id": lesson_id}


# ════════════════════════════════════════════════════════════
# MCP Tool Runtime — real MCP servers from the Loopfile TOOLS block
# ════════════════════════════════════════════════════════════
#
# The registry above is INFINI's built-in tool set. This layer is the
# runtime the MCP strategy (docs/mcp-strategy.md) specifies: it takes
# the Loopfile `TOOLS` entries (`- mcp: <ref>` + optional `config:`),
# launches each MCP server, discovers its tools over the protocol,
# namespaces them (`server.tool`), and routes calls to the owning
# server. Failures are classified the way the strategy doc names
# them: tool_unavailable / tool_timeout / tool_error / rate_limited.
#
# Transport in this implementation: stdio (the standard local MCP
# transport) via .mcp_client. Addressing modes resolve as follows:
#   - local path  → launched directly (see _resolve_command)
#   - github.com/…, URL, registry refs → resolved only when
#     config.command says how to launch the server locally;
#     otherwise the server is reported unavailable with the reason,
#     never silently skipped.
# Config values support ${VAR} environment substitution; resolved
# values are never logged or traced.

import os
import re
import shlex
import sys
import time
from dataclasses import dataclass, field

from .mcp_client import (
    McpStdioClient,
    McpTimeoutError,
    McpToolError,
    McpUnavailableError,
)

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class McpConfigError(Exception):
    """A TOOLS entry or its config is invalid (e.g. unset ${VAR})."""


@dataclass
class McpRef:
    """A parsed `mcp:` reference from a Loopfile TOOLS entry."""

    raw: str
    mode: str  # local | github | url | registry
    name: str  # short server name used for namespacing


def _normalize_name(name: str) -> str:
    name = name.strip().lower().replace("_", "-")
    return re.sub(r"[^a-z0-9.-]+", "-", name).strip("-") or "server"


def parse_mcp_ref(ref: str, config: dict | None = None) -> McpRef:
    """Parse an MCP server reference and derive its namespace name.

    An explicit `config.name` always wins; otherwise the name comes
    from the last path segment of the reference.
    """
    config = config or {}
    ref = str(ref).strip()
    if not ref:
        raise McpConfigError("empty MCP reference in TOOLS entry")

    if ref.startswith(("http://", "https://")):
        mode = "url"
        tail = ref.rstrip("/").split("/")[-1]
        default_name = tail or ref.split("/")[2].split(".")[0]
    elif ref.startswith("github.com/"):
        mode = "github"
        default_name = ref.rstrip("/").split("/")[-1]
        default_name = default_name.split("@")[0]
    elif ref.startswith(("./", "../", "/", "~")) or Path(ref).exists():
        mode = "local"
        p = Path(ref).expanduser()
        default_name = p.stem if p.suffix else p.name
    elif "/" in ref and "@" in ref:
        mode = "registry"
        default_name = ref.split("/")[-1].split("@")[0]
    else:
        mode = "registry"
        default_name = ref.split("@")[0]

    name = _normalize_name(str(config.get("name") or default_name))
    return McpRef(raw=ref, mode=mode, name=name)


def substitute_env(value: Any, environ: dict | None = None) -> Any:
    """Recursively expand ${VAR} in strings using the environment.

    Raises McpConfigError naming the missing variable (never its
    value) when a referenced variable is unset.
    """
    env = os.environ if environ is None else environ
    if isinstance(value, str):
        def _sub(match: re.Match) -> str:
            var = match.group(1)
            if var not in env:
                raise McpConfigError(
                    f"environment variable {var} is not set "
                    f"(referenced in MCP config)"
                )
            return env[var]
        return _ENV_PATTERN.sub(_sub, value)
    if isinstance(value, dict):
        return {k: substitute_env(v, env) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute_env(v, env) for v in value]
    return value


def plan_mcp_runtime(tools_entries: list[dict] | None) -> dict:
    """Describe the declared MCP servers without launching anything.

    Used by the deterministic (mock) engine so a trace records which
    servers a Loopfile declared. No config values are included.
    """
    servers = []
    for entry in tools_entries or []:
        ref = parse_mcp_ref(entry.get("mcp", ""), entry.get("config") or {})
        servers.append(
            {"mcp": ref.raw, "name": ref.name, "mode": ref.mode, "status": "declared"}
        )
    return {"servers": servers}


@dataclass
class McpServerHandle:
    """One MCP server: its ref, lifecycle status, and discovered tools."""

    entry: dict
    base_dir: Path | None = None
    ref: McpRef = field(init=False)
    config: dict = field(init=False)
    status: str = "pending"  # pending | ready | unavailable
    error: str | None = None
    tools: list[dict] = field(default_factory=list)  # namespaced defs
    _client: McpStdioClient | None = field(default=None, repr=False)
    _last_call_at: float = field(default=0.0, repr=False)
    total_cost: float = 0.0

    def __post_init__(self) -> None:
        raw_config = self.entry.get("config") or {}
        self.ref = parse_mcp_ref(self.entry.get("mcp", ""), raw_config)
        self.config = raw_config

    # ── lifecycle ────────────────────────────────────────────

    def start(self) -> bool:
        """Launch the server and discover its tools. Never raises:
        failures land in .status/.error so one dead server does not
        sink the whole loop (strategy doc: mark tool_unavailable)."""
        if self.status == "ready":
            return True
        try:
            config = substitute_env(self.config)
            command = self._resolve_command(config)
            env = dict(os.environ)
            for k, v in (config.get("env") or {}).items():
                env[str(k)] = str(v)
            cwd = config.get("cwd") or (
                str(self.base_dir) if self.base_dir else None
            )
            timeout = float(config.get("timeout_seconds", 30))
            self._client = McpStdioClient(
                command, env=env, cwd=cwd, request_timeout=timeout
            )
            self._client.start()
            raw_tools = self._client.list_tools()
        except (McpConfigError, McpUnavailableError, McpToolError,
                McpTimeoutError, ValueError) as e:
            self.status = "unavailable"
            self.error = str(e)
            self._client = None
            return False

        self.tools = [
            {
                "name": f"{self.ref.name}.{t.get('name', '')}",
                "description": t.get("description", ""),
                "parameters": t.get("inputSchema") or {"type": "object", "properties": {}},
                "mcp": self.ref.raw,
                "tool": t.get("name", ""),
            }
            for t in raw_tools
            if t.get("name")
        ]
        self.status = "ready"
        self.error = None
        return True

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # ── calls ────────────────────────────────────────────────

    def call(self, raw_tool: str, arguments: dict) -> dict:
        """Execute one tool call. Returns a classified call record."""
        started = time.monotonic()
        record: dict[str, Any] = {
            "mcp": self.ref.raw,
            "tool": f"{self.ref.name}.{raw_tool}",
        }
        if self.status != "ready" or self._client is None:
            record.update(ok=False, status="tool_unavailable",
                          error=self.error or "MCP server is not running")
            record["duration_ms"] = 0
            return record

        # Respect a declared rate_limit (max calls per second).
        rate = self.config.get("rate_limit")
        if rate:
            try:
                min_interval = 1.0 / float(rate)
                wait = min_interval - (time.monotonic() - self._last_call_at)
                if wait > 0:
                    time.sleep(wait)
            except (TypeError, ValueError):
                pass

        try:
            result = self._client.call_tool(raw_tool, arguments or {})
        except McpTimeoutError as e:
            record.update(ok=False, status="tool_timeout", error=str(e))
        except McpUnavailableError as e:
            self.status = "unavailable"
            self.error = str(e)
            record.update(ok=False, status="tool_unavailable", error=str(e))
        except McpToolError as e:
            record.update(ok=False, status="tool_error", error=str(e))
        else:
            if result.get("isError"):
                record.update(ok=False, status="tool_error",
                              error=_result_text(result) or "tool returned an error",
                              result=_normalize_result(result))
            else:
                record.update(ok=True, status="ok",
                              result=_normalize_result(result))
        self._last_call_at = time.monotonic()
        record["duration_ms"] = int((time.monotonic() - started) * 1000)
        cost = self.config.get("cost_per_call")
        if cost:
            try:
                record["cost"] = float(cost)
                self.total_cost += float(cost)
            except (TypeError, ValueError):
                pass
        return record

    # ── internals ────────────────────────────────────────────

    def _resolve_command(self, config: dict) -> list[str]:
        """Decide how to launch this server as a local process."""
        command = config.get("command")
        if command:
            if isinstance(command, str):
                return shlex.split(command)
            return [str(part) for part in command]

        if self.ref.mode == "local":
            p = Path(self.ref.raw).expanduser()
            if self.base_dir is not None and not p.is_absolute():
                p = self.base_dir / p
            if p.is_file():
                if p.suffix == ".py":
                    return [sys.executable, str(p)]
                return [str(p)]
            if p.is_dir():
                for candidate in ("server.py", "main.py", "__main__.py"):
                    entry = p / candidate
                    if entry.exists():
                        return [sys.executable, str(entry)]
                raise McpUnavailableError(
                    f"no server entry point (server.py/main.py) in {p}"
                )
            raise McpUnavailableError(f"local MCP path not found: {p}")

        raise McpUnavailableError(
            f"cannot resolve {self.ref.mode} reference {self.ref.raw!r} to a "
            f"local process; set config.command to launch it"
        )


def _result_text(result: dict) -> str:
    parts = []
    for item in result.get("content") or []:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text", "")))
    return "\n".join(parts)


def _normalize_result(result: dict) -> Any:
    """Flatten an MCP result into the most useful plain value."""
    if "structuredContent" in result:
        return result["structuredContent"]
    content = result.get("content")
    if isinstance(content, list):
        if len(content) == 1 and content[0].get("type") == "text":
            text = content[0].get("text", "")
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text
        texts = [c.get("text", "") for c in content
                 if isinstance(c, dict) and c.get("type") == "text"]
        if texts:
            return "\n".join(texts)
    return result


class McpToolRuntime:
    """Owns every MCP server declared by one Loopfile.

    Usage:
        runtime = McpToolRuntime(loopfile.tools, base_dir=loop_dir)
        runtime.start()
        defs = runtime.tools_for_agent(agent)
        record = runtime.call("notes.write_note", {"name": "x", "content": "y"})
        runtime.close()
    """

    def __init__(self, tools_entries: list[dict] | None,
                 base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else None
        self.servers: list[McpServerHandle] = [
            McpServerHandle(entry, base_dir=self.base_dir)
            for entry in (tools_entries or [])
        ]
        self._by_tool: dict[str, tuple[McpServerHandle, str]] = {}

    def start(self) -> dict:
        """Start all servers; returns the trace summary. Individual
        failures are recorded per server, never raised."""
        for server in self.servers:
            server.start()
            for tool_def in server.tools:
                self._by_tool[tool_def["name"]] = (server, tool_def["tool"])
        return self.trace_summary()

    def close(self) -> None:
        for server in self.servers:
            server.close()
        self._by_tool.clear()

    def __enter__(self) -> "McpToolRuntime":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ── discovery ────────────────────────────────────────────

    def tool_definitions(self) -> list[dict]:
        """All discovered tools, in the shape the engines already use
        ({name, description, parameters}) plus MCP provenance."""
        defs: list[dict] = []
        for server in self.servers:
            defs.extend(server.tools)
        return defs

    def tools_for_agent(self, agent) -> list[dict]:
        """The subset of discovered tools an agent declared in its
        `tools:` list (namespaced names, per spec §5b)."""
        declared = set(getattr(agent, "tools", []) or [])
        if not declared:
            return []
        return [d for d in self.tool_definitions() if d["name"] in declared]

    def has_tool(self, namespaced_name: str) -> bool:
        return namespaced_name in self._by_tool

    # ── execution ────────────────────────────────────────────

    def call(self, namespaced_name: str, arguments: dict | None = None) -> dict:
        """Route one namespaced tool call to its server.

        Returns a trace-shaped record:
        {mcp, tool, ok, status, result|error, duration_ms, cost?}
        """
        found = self._by_tool.get(namespaced_name)
        if found is None:
            # The server may exist but be unavailable (start failed);
            # answer tool_unavailable rather than "unknown" in that case.
            for server in self.servers:
                if namespaced_name.startswith(server.ref.name + "."):
                    raw = namespaced_name[len(server.ref.name) + 1:]
                    return server.call(raw, arguments or {})
            return {
                "mcp": None,
                "tool": namespaced_name,
                "ok": False,
                "status": "tool_error",
                "error": f"Unknown MCP tool: {namespaced_name}",
                "duration_ms": 0,
            }
        server, raw_tool = found
        return server.call(raw_tool, arguments or {})

    # ── reporting ────────────────────────────────────────────

    @property
    def total_cost(self) -> float:
        return round(sum(s.total_cost for s in self.servers), 6)

    def trace_summary(self) -> dict:
        """Per-server status for the trace. Config values (and any
        resolved secrets) are never included — names and refs only."""
        return {
            "servers": [
                {
                    "mcp": s.ref.raw,
                    "name": s.ref.name,
                    "mode": s.ref.mode,
                    "status": s.status,
                    "tools": [t["name"] for t in s.tools],
                    **({"error": s.error} if s.error else {}),
                }
                for s in self.servers
            ]
        }
