#!/usr/bin/env python3
# Copyright 2026 Moritz Foerster
# SPDX-License-Identifier: Apache-2.0
"""Serve the architecture viewer and one Markdown source file on localhost.

The source file holds a ```mermaid``` diagram and a step table. The page polls
for changes, so edits to the file show up without a reload.

Usage:
    python3 serve.py [SOURCE.md] [--port 8000] [--host 127.0.0.1] [--open]
"""

import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
SAMPLE_SOURCE = HERE / "sample_architecture.md"
# The project's own architecture when it sits next to the viewer, otherwise the bundled sample.
DEFAULT_SOURCE = HERE.parent / "architecture.md" if (HERE.parent / "architecture.md").is_file() else SAMPLE_SOURCE


def make_handler(source: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        # Only three routes. Nothing else on disk is reachable.
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self.reply(200, "text/html; charset=utf-8", INDEX.read_bytes())
            elif path == "/api/source":
                self.reply_source(include_text=True)
            elif path == "/api/mtime":
                self.reply_source(include_text=False)
            else:
                self.reply(404, "text/plain; charset=utf-8", b"not found")

        def reply_source(self, include_text: bool) -> None:
            try:
                payload = {"name": source.name, "mtime": source.stat().st_mtime}
                if include_text:
                    payload["text"] = source.read_text(encoding="utf-8")
            except OSError:
                body = json.dumps({"error": f"cannot read {source.name}"}).encode("utf-8")
                self.reply(404, "application/json; charset=utf-8", body)
                return
            self.reply(200, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))

        def reply(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            pass  # keep the terminal quiet while polling

    return Handler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the architecture viewer.")
    parser.add_argument("source", nargs="?", default=str(DEFAULT_SOURCE), help="Markdown file with a mermaid diagram and a step table (default: ../architecture.md, else sample_architecture.md)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: localhost only)")
    parser.add_argument("--open", action="store_true", help="Open the viewer in the default browser")
    args = parser.parse_args(argv)

    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        print(f"error: {source} is not a file", file=sys.stderr)
        return 2

    server = ThreadingHTTPServer((args.host, args.port), make_handler(source))
    url = f"http://{args.host}:{args.port}/"
    print(f"Serving {source.name} at {url}  (Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
