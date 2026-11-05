"""Tests for the MCP Tool Runtime (mcp_client + mcp_runtime layers).

The integration tests spawn a real MCP server subprocess
(mcp_test_server.py) and speak the actual protocol — initialize,
tools/list, tools/call — no protocol mocks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from infini.mcp_client import McpStdioClient, McpTimeoutError
from infini.mcp_runtime import (
    McpConfigError,
    McpToolRuntime,
    parse_mcp_ref,
    plan_mcp_runtime,
    substitute_env,
)
from infini.parse import parse

TEST_SERVER = Path(__file__).parent / "mcp_test_server.py"


def server_entry(**config):
    entry = {"mcp": str(TEST_SERVER), "config": {"name": "test", **config}}
    return entry


# ── reference parsing ────────────────────────────────────────

def test_parse_ref_github():
    ref = parse_mcp_ref("github.com/modelcontextprotocol/servers/src/filesystem")
    assert ref.mode == "github"
    assert ref.name == "filesystem"


def test_parse_ref_local_with_name_override():
    ref = parse_mcp_ref("./servers/notes_server.py", {"name": "notes"})
    assert ref.mode == "local"
    assert ref.name == "notes"


def test_parse_ref_url():
    ref = parse_mcp_ref("https://mcp.example.com/servers/postgres")
    assert ref.mode == "url"
    assert ref.name == "postgres"


def test_parse_ref_registry():
    ref = parse_mcp_ref("infini/mcp/postgres@1.2")
    assert ref.mode == "registry"
    assert ref.name == "postgres"


def test_parse_ref_empty_raises():
    with pytest.raises(McpConfigError):
        parse_mcp_ref("")


# ── env substitution ─────────────────────────────────────────

def test_substitute_env_expands_and_recurses():
    env = {"DB_URL": "postgres://localhost/db"}
    out = substitute_env({"cs": "${DB_URL}", "n": 3, "l": ["${DB_URL}"]}, env)
    assert out == {"cs": "postgres://localhost/db", "n": 3,
                   "l": ["postgres://localhost/db"]}


def test_substitute_env_missing_var_raises_without_value():
    with pytest.raises(McpConfigError) as exc:
        substitute_env("${DEFINITELY_UNSET_VAR}", {})
    assert "DEFINITELY_UNSET_VAR" in str(exc.value)


# ── plan (no launch) ─────────────────────────────────────────

def test_plan_records_declared_servers():
    plan = plan_mcp_runtime([
        {"mcp": "github.com/modelcontextprotocol/servers/src/github"},
        {"mcp": "./notes_server.py", "config": {"name": "notes"}},
    ])
    assert [s["name"] for s in plan["servers"]] == ["github", "notes"]
    assert all(s["status"] == "declared" for s in plan["servers"])


# ── client round trip ────────────────────────────────────────

def test_client_round_trip():
    with McpStdioClient([sys.executable, str(TEST_SERVER)]) as client:
        assert client.server_info["name"] == "infini-test-server"
        tools = client.list_tools()
        assert {t["name"] for t in tools} == {"echo", "add", "fail", "sleep"}
        assert client.ping() is True
        result = client.call_tool("echo", {"text": "hello"})
        assert result["content"][0]["text"] == "hello"


def test_client_timeout():
    client = McpStdioClient(
        [sys.executable, str(TEST_SERVER)], request_timeout=0.3
    )
    client.start()
    try:
        with pytest.raises(McpTimeoutError):
            client.call_tool("sleep", {"seconds": 5})
    finally:
        client.close()


# ── runtime integration ──────────────────────────────────────

def test_runtime_discovers_namespaced_tools_and_calls():
    with McpToolRuntime([server_entry()]) as runtime:
        summary = runtime.trace_summary()
        assert summary["servers"][0]["status"] == "ready"
        names = {d["name"] for d in runtime.tool_definitions()}
        assert names == {"test.echo", "test.add", "test.fail", "test.sleep"}

        rec = runtime.call("test.add", {"a": 2, "b": 40})
        assert rec["ok"] is True
        assert rec["status"] == "ok"
        assert rec["result"] == {"sum": 42}
        assert rec["mcp"] == str(TEST_SERVER)
        assert rec["duration_ms"] >= 0


def test_runtime_tool_error_classification():
    with McpToolRuntime([server_entry()]) as runtime:
        rec = runtime.call("test.fail", {})
        assert rec["ok"] is False
        assert rec["status"] == "tool_error"
        assert "deliberate failure" in rec["error"]


def test_runtime_timeout_classification():
    with McpToolRuntime([server_entry(timeout_seconds=0.3)]) as runtime:
        rec = runtime.call("test.sleep", {"seconds": 5})
        assert rec["ok"] is False
        assert rec["status"] == "tool_timeout"


def test_runtime_unknown_tool():
    with McpToolRuntime([server_entry()]) as runtime:
        rec = runtime.call("test.nope", {})
        assert rec["ok"] is False
        assert rec["status"] == "tool_error"


def test_runtime_unavailable_server_is_reported_not_raised():
    entry = {"mcp": "./does-not-exist-server.py", "config": {"name": "ghost"}}
    runtime = McpToolRuntime([entry], base_dir=Path(__file__).parent)
    summary = runtime.start()
    try:
        assert summary["servers"][0]["status"] == "unavailable"
        assert summary["servers"][0]["error"]
        rec = runtime.call("ghost.anything", {})
        assert rec["ok"] is False
        assert rec["status"] == "tool_unavailable"
    finally:
        runtime.close()


def test_runtime_remote_ref_without_command_is_unavailable():
    entry = {"mcp": "github.com/modelcontextprotocol/servers/src/postgres"}
    runtime = McpToolRuntime([entry])
    summary = runtime.start()
    try:
        assert summary["servers"][0]["status"] == "unavailable"
        assert "config.command" in summary["servers"][0]["error"]
    finally:
        runtime.close()


def test_runtime_config_command_and_env_substitution(monkeypatch):
    monkeypatch.setenv("INFINI_TEST_MARKER", "from-env")
    entry = {
        "mcp": "registry://anything",
        "config": {
            "name": "viacmd",
            "command": [sys.executable, str(TEST_SERVER)],
            "env": {"MARKER": "${INFINI_TEST_MARKER}"},
        },
    }
    with McpToolRuntime([entry]) as runtime:
        assert runtime.trace_summary()["servers"][0]["status"] == "ready"
        assert runtime.has_tool("viacmd.echo")
        # trace summary must never carry config values / secrets
        assert "from-env" not in str(runtime.trace_summary())


def test_runtime_missing_env_var_marks_server_unavailable(monkeypatch):
    monkeypatch.delenv("INFINI_TEST_UNSET", raising=False)
    entry = {
        "mcp": str(TEST_SERVER),
        "config": {"name": "needsenv", "env": {"X": "${INFINI_TEST_UNSET}"}},
    }
    runtime = McpToolRuntime([entry])
    summary = runtime.start()
    try:
        assert summary["servers"][0]["status"] == "unavailable"
        assert "INFINI_TEST_UNSET" in summary["servers"][0]["error"]
    finally:
        runtime.close()


def test_runtime_tools_for_agent_filters_by_declaration():
    class FakeAgent:
        tools = ["test.echo"]

    with McpToolRuntime([server_entry()]) as runtime:
        defs = runtime.tools_for_agent(FakeAgent())
        assert [d["name"] for d in defs] == ["test.echo"]


# ── Loopfile integration ─────────────────────────────────────

LOOPFILE_WITH_TOOLS = """
LOOPFILE: "1.0"
name: mcp-test-loop
version: 1.0.0
OBJECTIVE: "Exercise the TOOLS block."
TOOLS:
  - mcp: "./notes_server.py"
    config: { name: "notes" }
AGENTS:
  - { name: scribe, role: researcher, model_tier: sonnet, tools: [notes.write_note] }
STEPS:
  - { id: s1, name: take_notes, action: write_notes, uses: scribe, produces: [notes.md] }
VERIFY:
  syntactic: ["notes.md:exists"]
  semantic: ["judge:correctness>=80"]
  confidence_threshold: 80
BUDGET: { dollars: 5, minutes: 5 }
STOP_WHEN: ["all_verify_passed", "iterations>=2"]
"""


def test_parse_populates_tools_and_round_trips():
    from infini.parse import to_dict
    lf = parse(LOOPFILE_WITH_TOOLS)
    assert lf.tools == [
        {"mcp": "./notes_server.py", "config": {"name": "notes"}}
    ]
    assert to_dict(lf)["TOOLS"] == lf.tools


def test_mock_engine_records_mcp_plan_in_trace(tmp_path):
    from infini.engine import run
    lf = parse(LOOPFILE_WITH_TOOLS)
    trace = run(lf, output_dir=tmp_path, mock=True, verbose=False,
                deterministic=True)
    servers = trace.extensions["mcp"]["servers"]
    assert servers[0]["name"] == "notes"
    assert servers[0]["status"] == "declared"
    assert trace.outcome == "verified"
