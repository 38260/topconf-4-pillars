#!/usr/bin/env python3
"""Re-hit the official sources for the 48 curated papers, then rebuild outputs.

Used by POST /api/refresh. Kept separate from build_papers.py so the offline
path (data/draft.json cache) stays the default and this only runs on demand.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, SCRIPTS)

from build_papers import resolve  # noqa: E402
from fetchlib import http  # noqa: E402


def main() -> int:
    http.RAW_DIR = os.path.join(DATA, "raw")
    papers = resolve(use_cache=False)
    old_path = os.path.join(DATA, "draft.json")
    old = {}
    if os.path.exists(old_path):
        old = {p["id"]: p for p in json.load(open(old_path, encoding="utf-8"))}

    changed = 0
    for p in papers:
        prev = old.get(p["id"])
        if prev and prev.get("abstract") != p.get("abstract"):
            changed += 1
            print(f"  ~ 官方摘要已变化: {p['id']}")
        if not p.get("abstract") and prev:
            p["abstract"] = prev["abstract"]  # never regress to empty on a network hiccup

    with open(old_path, "w", encoding="utf-8") as fh:
        json.dump(papers, fh, ensure_ascii=False, indent=2)
    print(f"refreshed {len(papers)} papers ({changed} changed)")

    for script in ("build_papers.py", "build_data.py"):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)],
                           cwd=ROOT, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            print(f"{script} failed")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
