"""Opt-in anonymous telemetry for INFINI."""
import threading
import urllib.request
import urllib.parse
import json

def emit_run_telemetry(engine: str, trace_outcome: str, loopfile_name: str, mock: bool):
    """Fire and forget a telemetry ping."""
    def _send():
        try:
            data = json.dumps({
                "engine": engine,
                "outcome": trace_outcome,
                "loopfile": loopfile_name,
                "mock": mock
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "https://api.infini.dev/telemetry/run",
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "infini-cli/1.0"},
                method="POST"
            )
            # Timeout fast so we don't block
            urllib.request.urlopen(req, timeout=1.5)
        except Exception:
            pass # Swallow errors to stay silent
            
    # Run in thread to not block CLI exit
    threading.Thread(target=_send, daemon=True).start()
