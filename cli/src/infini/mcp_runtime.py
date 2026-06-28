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
