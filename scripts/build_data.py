#!/usr/bin/env python3
"""Inject data/papers.json into web/data/papers.js.

A JS global (not fetch) so the page also works when opened directly as file://
with no local server. Regenerate after any change to papers.json.
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "papers.json")
OUT = os.path.join(ROOT, "web", "data", "papers.js")


def main() -> int:
    data = json.load(open(SRC, encoding="utf-8"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("/* 由 scripts/build_data.py 从 data/papers.json 生成，请勿手改。 */\n")
        fh.write("window.PAPERS_DATA = " + body + ";\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.1f} KB, {len(data['papers'])} papers)")
    # keep a copy for the served /api path too
    jout = os.path.join(ROOT, "web", "data", "papers.json")
    with open(jout, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"wrote {jout}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
