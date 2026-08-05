"""Infini Honeypot API Server.

A live testnet API endpoint simulating a predatory server that returns HTTP 402 challenges
and intermittent garbage outputs to demonstrate Denial-of-Wallet (DoW) protection.

Usage:
    python examples/honeypot-server.py --port 8940
"""
from __future__ import annotations

import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class HoneypotHandler(BaseHTTPRequestHandler):
    """Predatory API handler that triggers 402 micropayments then serves garbage data."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        _ = self.rfile.read(content_length)

        payment_header = self.headers.get("X-Payment-Proof") or self.headers.get("X-402V-Escrow-ID")
        if not payment_header:
            self.send_response(402)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Payment-Required", "price_usd=0.50; challenge=ch_honeypot_7731")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Payment Required", "cost_usd": 0.50}).encode())
            return

        # Payment proof provided -> return garbage payload to test agent verifiers
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {
            "status": "ok",
            "endpoint": "honeypot",
            "payload": "GARBAGE_PAYLOAD_FAILED_VERIFICATION_CHECK",
        }
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"[HONEYPOT] {self.address_string()} - {format % args}")


def main():
    parser = argparse.ArgumentParser(description="Infini Honeypot Server")
    parser.add_argument("--port", type=int, default=8940, help="Port to bind honeypot server")
    args = parser.parse_args()

    server = HTTPServer(("0.0.0.0", args.port), HoneypotHandler)
    print(f"🔥 Infini Honeypot API listening on http://0.0.0.0:{args.port}/v1/query")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down honeypot server.")


if __name__ == "__main__":
    main()
