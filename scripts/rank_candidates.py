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
    args = ap.parse_args()

    corpus = json.load(open(os.path.join(DATA, "corpus.json"), encoding="utf-8"))
    out = ["# 候选清单（脚本生成，供人工精选）", "",
           "打分：标题命中 x3 + 摘要命中 x1。AAAI 摘要随语料落地，"
           "CVPR/ICCV/ACL 在 build_papers 阶段回源补官方摘要。", ""]

    for venue in args.venues.split(","):
        rows = corpus["papers"][venue]
        # only consider records whose text we can actually read
        pool = [r for r in rows if r.get("abstract")] if venue == "AAAI" else rows
        out.append(f"\n## {venue} · 语料 {len(rows)} 篇（本次打分 {len(pool)}）\n")
        for topic in TOPICS:
            compiled = [re.compile(p, re.I) for p in topic["patterns"]]
            scored = []
            for r in pool:
                s, h = score(r, compiled)
                if h:
                    scored.append((s, r))
            scored.sort(key=lambda x: -x[0])
            top = scored[: args.per_topic]
            out.append(f"### {topic['label']} `{topic['id']}` — 命中 {len(scored)}")
            out.append("")
            for s, r in top:
                extra = r.get("volume") or r.get("pages") or ""
                out.append(f"- `{r['paper_id']}` ({s:.0f}) {r['title']}"
                           + (f" — _{extra}_" if extra else ""))
            out.append("")
        # also list generic deep-learning-method papers with no topic winner, for coverage
    path = os.path.join(DATA, "candidates.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", path, os.path.getsize(path), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
