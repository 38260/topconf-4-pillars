#!/usr/bin/env python3
"""Rank corpus candidates per venue x topic -> data/candidates.md (review sheet).

Deterministic and reproducible: title keyword hits weigh 3x abstract hits,
papers without an official abstract sink to the bottom. Hand-picking happens
in data/selection.json, so the sheet only narrows 16k papers down to ~10.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import TOPICS, match_topics  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def score(rec: dict, compiled: list) -> tuple[float, int]:
    title = rec["title"]
    abstract = rec.get("abstract") or ""
    hits = 0
    s = 0.0
    for pat in compiled:
        t = len(pat.findall(title))
        a = len(pat.findall(abstract))
        hits += t + a
        s += t * 3 + a
    return s, hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-topic", type=int, default=6)
    ap.add_argument("--venues", default="CVPR,AAAI,ICCV,ACL")
    ap.add_argument("--years", default="", help="comma list, e.g. 2024,2025")
    ap.add_argument("--skip-curated", action="store_true",
                    help="drop paper_ids already picked in data/selection.json")
    args = ap.parse_args()

    curated = set()
    sel_path = os.path.join(DATA, "selection.json")
    if args.skip_curated and os.path.exists(sel_path):
        curated = {p["ref"] for p in json.load(open(sel_path, encoding="utf-8"))["papers"]}
    want_years = {int(y) for y in args.years.split(",") if y.strip()}

    corpus = json.load(open(os.path.join(DATA, "corpus.json"), encoding="utf-8"))
    out = ["# 候选清单（脚本生成，供人工精选）", "",
           "打分：标题命中 x3 + 摘要命中 x1。AAAI 摘要随语料落地，"
           "CVPR/ICCV/ACL 在 build_papers 阶段回源补官方摘要。", ""]

    for venue in args.venues.split(","):
        allrows = corpus["papers"][venue]
        for year in sorted({r["year"] for r in allrows}):
            if want_years and year not in want_years:
                continue
            rows = [r for r in allrows if r["year"] == year]
            if curated:
                rows = [r for r in rows if r["paper_id"] not in curated]
            # only score on text we actually have: AAAI ships abstracts in the corpus
            pool = [r for r in rows if r.get("abstract")] if venue == "AAAI" else rows
            out.append(f"\n## {venue} {year} · 语料 {len(rows)} 篇（本次打分 {len(pool)}）\n")
            for topic in TOPICS:
                compiled = [re.compile(p, re.I) for p in topic["patterns"]]
                scored = []
                for r in pool:
                    sc, h = score(r, compiled)
                    if h:
                        scored.append((sc, r))
                scored.sort(key=lambda x: -x[0])
                out.append(f"### {topic['label']} `{topic['id']}` — 命中 {len(scored)}")
                out.append("")
                for sc, r in scored[: args.per_topic]:
                    extra = r.get("volume") or r.get("pages") or ""
                    out.append(f"- `{r['paper_id']}` ({sc:.0f}) {r['title']}"
                               + (f" — _{extra}_" if extra else ""))
                out.append("")
    path = os.path.join(DATA, "candidates.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", path, os.path.getsize(path), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
