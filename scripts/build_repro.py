#!/usr/bin/env python3
"""Merge web/data/repro/batch-*.json into data/repro.json, then inject into web/data/repro.js.

与 build_data.py 同构：repro.js 以 JS 全局注入，file:// 离线可打开。
用法：
  python scripts/build_repro.py           # 仅从 data/repro.json 重新生成 repro.js
  python scripts/build_repro.py --merge   # 先合并批次调研结果，再生成
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "repro.json")
BATCH_DIR = os.path.join(ROOT, "web", "data", "repro")
OUT_JS = os.path.join(ROOT, "web", "data", "repro.js")

FIELDS = ("github", "github_official", "github_stars", "no_code",
          "datasets", "difficulty", "compute", "reason")


def merge() -> dict:
    existing = {}
    if os.path.exists(SRC):
        existing = json.load(open(SRC, encoding="utf-8")).get("papers", {})
    papers = dict(existing)
    ids = {p["id"] for p in json.load(open(os.path.join(ROOT, "data", "papers.json"),
                                           encoding="utf-8"))["papers"]}
    unknown, n = [], 0
    for path in sorted(glob.glob(os.path.join(BATCH_DIR, "batch-[0-9][0-9].json"))):
        batch = json.load(open(path, encoding="utf-8"))
        items = batch if isinstance(batch, list) else batch.get("papers", [])
        for item in items:
            pid = item.get("id")
            if pid not in ids:
                unknown.append((os.path.basename(path), pid))
                continue
            entry = {k: item.get(k) for k in FIELDS if item.get(k) is not None}
            entry["source_batch"] = os.path.basename(path)
            papers[pid] = entry
            n += 1
    out = {"generated_at": None, "note": "外部调研（GitHub/数据集/算力）派生信息，非出版方数据",
           "papers": papers}
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    with open(SRC, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"merged {n} entries -> {SRC} (total {len(papers)})")
    if unknown:
        print("skipped unknown ids:")
        for b, pid in unknown:
            print(f"  {b}: {pid}")
    return out


def inject(data: dict) -> int:
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with open(OUT_JS, "w", encoding="utf-8") as fh:
        fh.write("/* 由 scripts/build_repro.py 从 data/repro.json 生成，请勿手改。 */\n")
        fh.write("window.REPRO_DATA = " + body + ";\n")
    print(f"wrote {OUT_JS} ({os.path.getsize(OUT_JS) / 1024:.1f} KB, "
          f"{len(data.get('papers', {}))} entries)")
    return 0


def main() -> int:
    if "--merge" in sys.argv:
        data = merge()
    else:
        if not os.path.exists(SRC):
            print("data/repro.json 不存在，请先 --merge", file=sys.stderr)
            return 1
        data = json.load(open(SRC, encoding="utf-8"))
    return inject(data)


if __name__ == "__main__":
    raise SystemExit(main())
