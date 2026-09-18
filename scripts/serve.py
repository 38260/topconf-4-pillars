#!/usr/bin/env python3
"""Local server: static site + native API (no third-party dependency).

  python scripts/serve.py [--port 8765] [--reload]

  GET  /              -> web/index.html
  GET  /api/papers    -> data/papers.json
  POST /api/refresh   -> re-fetch the official sources, rebuild, return payload
  GET  /api/health    -> {ok, papers, served_at}

Binds to 127.0.0.1 only; /api/refresh is the one endpoint that touches the network.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "TopConfPillars/1.0"

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   TYPES[".json"])

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            papers = _load_papers()
            return self._json(200, {"ok": True,
                                    "papers": len(papers.get("papers", [])),
                                    "served_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        if path == "/api/papers":
            return self._json(200, _load_papers())
        return self._static(path)

    def do_POST(self):  # noqa: N802
        if urlparse(self.path).path != "/api/refresh":
            return self._json(404, {"error": "not found"})
        try:
            out = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "refresh.py")],
                capture_output=True, text=True, timeout=600, cwd=ROOT)
            if out.returncode != 0:
                return self._json(500, {"error": (out.stderr or out.stdout)[-600:]})
            return self._json(200, _load_papers())
        except Exception as exc:  # noqa: BLE001
            return self._json(500, {"error": str(exc)})

    def _static(self, path: str):
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = os.path.normpath(os.path.join(WEB, rel))
        if not target.startswith(WEB) or not os.path.isfile(target):
            return self._send(404, b"404 not found", "text/plain; charset=utf-8")
        ext = os.path.splitext(target)[1].lower()
        with open(target, "rb") as fh:
            return self._send(200, fh.read(), TYPES.get(ext, "application/octet-stream"))

    def log_message(self, fmt, *args):  # quieter default log
        sys.stderr.write("  %s\n" % (fmt % args))


def _load_papers() -> dict:
    for cand in (os.path.join(ROOT, "data", "papers.json"),
                 os.path.join(WEB, "data", "papers.json")):
        if os.path.exists(cand):
            with open(cand, encoding="utf-8") as fh:
                return json.load(fh)
    return {"papers": [], "meta": {"error": "papers.json missing"}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"顶会四支柱看板 -> http://127.0.0.1:{args.port}/   (Ctrl+C 停止)")
    print(f"数据源：{len(_load_papers().get('papers', []))} 篇精选 · API /api/papers")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
