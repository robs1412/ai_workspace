#!/usr/local/bin/python3.13
"""Local-only web server for the Family AI Class demo."""

from __future__ import annotations

import http.server
import socketserver


HOST = "127.0.0.1"
PORT = 8765


class Handler(http.server.SimpleHTTPRequestHandler):
    pass


def main() -> int:
    with socketserver.TCPServer((HOST, PORT), Handler) as server:
        print(f"Serving local demo at http://{HOST}:{PORT}")
        print("Press Control-C to stop.")
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
