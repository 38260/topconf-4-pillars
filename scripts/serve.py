#!/usr/bin/env python3
"""Local server: static site + native API (no third-party dependency).

  python scripts/serve.py [--port 8765] [--reload]

  GET  /              -> web/index.html
  GET  /api/papers    -> data/papers.json
  POST /api/refresh   -> re-fetch the official sources, rebuild, return payload
  GET  /api/favs      -> {exists, ids, updated_at}   收藏（落盘 data/favs.json）
  POST /api/favs      -> 覆盖写入收藏；若服务端时间戳更新则返回 409 + 现存数据
  GET  /api/health    -> {ok, papers, favs, served_at}

Binds to 127.0.0.1 only; /api/refresh is the one endpoint that touches the network.

收藏为什么要落盘：localStorage 按「协议 + 端口」隔离，换端口（start.bat 8790）、
换浏览器、清缓存都会让收藏凭空消失。落盘后换浏览器、换端口都能读回同一份收藏。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
SCRIPTS = os.path.join(ROOT, "scripts")
FAVS = os.path.join(ROOT, "data", "favs.json")
MAX_FAVS = 5000          # 收藏条数上限（防御异常请求写爆文件）
MAX_FAV_LEN = 200        # 单个 id 长度上限
MAX_BODY = 1 << 20       # 请求体 1 MB 上限
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
                                    "favs": len(_load_favs()["ids"]),
                                    "served_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        if path == "/api/papers":
            return self._json(200, _load_papers())
        if path == "/api/favs":
            return self._json(200, _load_favs())
        if path == "/api/export":
            return self._export(parse_qs(urlparse(self.path).query))
        return self._static(path)

    def _export(self, qs) -> None:
        fmt = (qs.get("fmt") or ["bib"])[0]
        if fmt not in ("bib", "ris", "md"):
            return self._json(400, {"error": "fmt must be bib|ris|md"})
        blob = _load_papers()
        papers = blob.get("papers", [])
        ids = (qs.get("ids") or [""])[0]
        venue = (qs.get("venue") or [""])[0]
        if ids:
            want = {i for i in ids.split(",") if i}
            subset = [p for p in papers if p["id"] in want]
        elif venue:
            subset = [p for p in papers if p["venue"] == venue]
        else:
            subset = papers
        if not subset:
            return self._json(404, {"error": "no papers matched"})
        if SCRIPTS not in sys.path:
            sys.path.insert(0, SCRIPTS)
        from fetchlib import citation
        text, ctype = citation.render_bundle(subset, fmt)
        fname = (venue or "selection").lower() + "." + fmt
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/favs":
            return self._favs_post()
        if path != "/api/refresh":
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

    def _favs_post(self) -> None:
        """覆盖写入收藏。时间戳更旧的一方不覆盖服务端，返回 409 让客户端采纳。"""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._json(400, {"error": "bad Content-Length"})
        if length <= 0 or length > MAX_BODY:
            return self._json(400, {"error": "body missing or too large"})
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:  # noqa: BLE001
            return self._json(400, {"error": "invalid json body"})
        if not isinstance(payload, dict):
            return self._json(400, {"error": "body must be an object"})
        ids = _clean_ids(payload.get("ids"))
        try:
            at = int(payload.get("updated_at") or 0)
        except (TypeError, ValueError):
            at = 0
        if at <= 0:
            at = int(time.time() * 1000)
        current = _load_favs()
        if current["exists"] and current["updated_at"] > at:
            return self._json(409, dict(current, conflict="server_newer"))
        return self._json(200, _save_favs(ids, at))

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


def _load_favs() -> dict:
    """读收藏。文件不存在（首次运行）与文件损坏要区分开，损坏时不静默清空。"""
    try:
        with open(FAVS, encoding="utf-8") as fh:
            obj = json.load(fh)
    except FileNotFoundError:
        return {"exists": False, "ids": [], "updated_at": 0}
    except Exception as exc:  # noqa: BLE001
        return {"exists": False, "ids": [], "updated_at": 0,
                "error": "data/favs.json 无法解析（未改动该文件）：%s" % exc}
    if not isinstance(obj, dict):
        return {"exists": False, "ids": [], "updated_at": 0,
                "error": "data/favs.json 结构异常（未改动该文件）"}
    try:
        at = int(obj.get("updated_at") or 0)
    except (TypeError, ValueError):
        at = 0
    return {"exists": True, "ids": _clean_ids(obj.get("ids")), "updated_at": at,
            "saved_at": obj.get("saved_at")}


def _save_favs(ids, updated_at: int) -> dict:
    """原子落盘：先写 .tmp 再 os.replace，避免半截文件把收藏写坏。"""
    os.makedirs(os.path.dirname(FAVS), exist_ok=True)
    payload = {"ids": ids, "updated_at": int(updated_at),
               "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    tmp = FAVS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, FAVS)
    return dict(payload, exists=True)


def _clean_ids(raw) -> list:
    """入参净化：只留非空字符串、去重、限长限量（防御异常请求）。"""
    out, seen = [], set()
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, str):
            continue
        key = item.strip()
        if not key or len(key) > MAX_FAV_LEN or key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= MAX_FAVS:
            break
    return out


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
