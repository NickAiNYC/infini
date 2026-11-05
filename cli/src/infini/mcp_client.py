"""Minimal MCP client — JSON-RPC 2.0 over stdio.

Speaks the Model Context Protocol (https://modelcontextprotocol.io)
to a server running as a subprocess: newline-delimited JSON-RPC on
stdin/stdout, the standard MCP stdio transport.

Implemented with the standard library only, in keeping with the CLI's
"no heavy dependency" rule (see mcp_runtime.py). This client covers
the tool surface INFINI needs: initialize, tools/list, tools/call,
ping, and orderly shutdown.

Attribution: protocol shape follows the MCP specification
(2025-03-26); client structure is original to INFINI.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from typing import Any

PROTOCOL_VERSION = "2025-03-26"
CLIENT_INFO = {"name": "infini-cli", "version": "1.1.0"}


class McpError(Exception):
    """Base class for MCP client errors."""


class McpUnavailableError(McpError):
    """The server process could not be started or died mid-session."""


class McpTimeoutError(McpError):
    """A request did not complete within the configured timeout."""


class McpProtocolError(McpError):
    """The server sent malformed JSON-RPC."""


class McpToolError(McpError):
    """The server returned a JSON-RPC error for a request."""


class _Pending:
    __slots__ = ("event", "result", "error")

    def __init__(self) -> None:
        self.event = threading.Event()
        self.result: Any = None
        self.error: BaseException | None = None


class McpStdioClient:
    """An MCP client session with one server subprocess.

    Usage:
        client = McpStdioClient(["python3", "server.py"])
        client.start()
        tools = client.list_tools()
        result = client.call_tool("echo", {"text": "hi"})
        client.close()
    """

    def __init__(
        self,
        command: list[str],
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        request_timeout: float = 30.0,
    ) -> None:
        if not command:
            raise McpUnavailableError("empty server command")
        self.command = list(command)
        self.env = env
        self.cwd = cwd
        self.request_timeout = request_timeout
        self.server_info: dict = {}
        self.protocol_version: str | None = None
        self._proc: subprocess.Popen | None = None
        self._next_id = 1
        self._id_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._pending: dict[int, _Pending] = {}
        self._pending_lock = threading.Lock()
        self._reader: threading.Thread | None = None
        self._closed = False

    # ── lifecycle ────────────────────────────────────────────────

    def start(self) -> dict:
        """Spawn the server and run the initialize handshake.

        Returns the server's initialize result. Raises
        McpUnavailableError if the process cannot start or the
        handshake fails.
        """
        if self._proc is not None:
            raise McpError("client already started")
        try:
            self._proc = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                env=self.env,
                cwd=self.cwd,
            )
        except (FileNotFoundError, PermissionError, OSError) as e:
            raise McpUnavailableError(
                f"could not start MCP server {self.command!r}: {e}"
            ) from e

        self._reader = threading.Thread(
            target=self._read_loop, name="mcp-stdio-reader", daemon=True
        )
        self._reader.start()

        try:
            result = self._request(
                "initialize",
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": CLIENT_INFO,
                },
            )
        except McpError as e:
            self.close()
            raise McpUnavailableError(f"MCP initialize failed: {e}") from e

        self.server_info = result.get("serverInfo", {}) if isinstance(result, dict) else {}
        self.protocol_version = (
            result.get("protocolVersion") if isinstance(result, dict) else None
        )
        self._notify("notifications/initialized", {})
        return result

    def close(self) -> None:
        """Shut the session down: close stdin, then terminate if needed."""
        if self._closed:
            return
        self._closed = True
        proc, self._proc = self._proc, None
        if proc is None:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
        self._fail_all_pending(McpUnavailableError("MCP session closed"))

    def __enter__(self) -> "McpStdioClient":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @property
    def is_running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    # ── protocol surface ─────────────────────────────────────────

    def ping(self) -> bool:
        """Round-trip a ping. Returns True on success."""
        self._request("ping", {})
        return True

    def list_tools(self) -> list[dict]:
        """Return the server's tool list (raw MCP tool objects)."""
        result = self._request("tools/list", {})
        if not isinstance(result, dict) or "tools" not in result:
            raise McpProtocolError(f"tools/list returned unexpected payload: {result!r}")
        return result["tools"]

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        """Call a tool. Returns the raw MCP result object.

        Raises McpToolError on a JSON-RPC error response. A result
        with ``isError: true`` is returned, not raised — the caller
        (runtime layer) classifies it.
        """
        result = self._request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        if not isinstance(result, dict):
            raise McpProtocolError(f"tools/call returned unexpected payload: {result!r}")
        return result

    # ── transport internals ──────────────────────────────────────

    def _read_loop(self) -> None:
        proc = self._proc
        assert proc is not None and proc.stdout is not None
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue  # not JSON-RPC; servers must not do this, but don't die
                self._dispatch(msg)
        except (ValueError, OSError):
            pass
        finally:
            self._fail_all_pending(
                McpUnavailableError("MCP server process exited")
            )

    def _dispatch(self, msg: dict) -> None:
        if not isinstance(msg, dict):
            return
        msg_id = msg.get("id")
        if msg_id is None:
            return  # notification from the server; nothing to fulfill
        with self._pending_lock:
            pending = self._pending.pop(msg_id, None)
        if pending is None:
            return  # response to something we stopped waiting for
        if "error" in msg and msg["error"] is not None:
            err = msg["error"]
            detail = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            pending.error = McpToolError(f"server error: {detail}")
        else:
            pending.result = msg.get("result")
        pending.event.set()

    def _fail_all_pending(self, error: BaseException) -> None:
        with self._pending_lock:
            pending = list(self._pending.values())
            self._pending.clear()
        for p in pending:
            if not p.event.is_set():
                p.error = error
                p.event.set()

    def _send(self, payload: dict) -> None:
        proc = self._proc
        if proc is None or proc.stdin is None or self._closed:
            raise McpUnavailableError("MCP session is not running")
        line = json.dumps(payload)
        with self._write_lock:
            try:
                proc.stdin.write(line + "\n")
                proc.stdin.flush()
            except (BrokenPipeError, OSError) as e:
                raise McpUnavailableError(f"could not write to MCP server: {e}") from e

    def _request(self, method: str, params: dict, timeout: float | None = None) -> Any:
        if self._proc is None:
            raise McpUnavailableError("MCP client not started")
        with self._id_lock:
            req_id = self._next_id
            self._next_id += 1
        pending = _Pending()
        with self._pending_lock:
            self._pending[req_id] = pending
        try:
            self._send(
                {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
            )
        except McpError:
            with self._pending_lock:
                self._pending.pop(req_id, None)
            raise
        wait = self.request_timeout if timeout is None else timeout
        if not pending.event.wait(wait):
            with self._pending_lock:
                self._pending.pop(req_id, None)
            raise McpTimeoutError(
                f"MCP request {method} timed out after {wait:.1f}s"
            )
        if pending.error is not None:
            raise pending.error
        return pending.result

    def _notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})


def _self_check() -> int:  # pragma: no cover - manual smoke entry point
    print("mcp_client imports cleanly", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_self_check())
