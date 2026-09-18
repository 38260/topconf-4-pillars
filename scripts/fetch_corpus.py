#!/usr/bin/env python3
"""Fetch the full official paper listing of all four pillars -> data/corpus.json.

Run:  python scripts/fetch_corpus.py [--no-cache]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetchlib import acl_anthology, cvf, http, openalex  # noqa: E402
from pillars import PILLARS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def fetch_all(use_cache: bool = True) -> dict:
    buckets: dict[str, list] = {}

    for key in ("CVPR", "ICCV"):
        pillar = next(p for p in PILLARS if p["key"] == key)
        print(f"[CVF] {pillar['label']} {pillar['year']} …")
        rows = cvf.index(key, use_cache=use_cache)
        print(f"  · {len(rows)} papers")
        buckets[key] = rows

    print("[ACL] discovering volumes …")
    vols = acl_anthology.discover_volumes()
    print(f"  · volumes: {', '.join(vols)}")
    buckets["ACL"] = acl_anthology.index(vols, use_cache=use_cache)
    print(f"  · {len(buckets['ACL'])} papers")

    pillar = next(p for p in PILLARS if p["key"] == "AAAI")
    print(f"[OpenAlex] AAAI {pillar['year']} …")
    buckets["AAAI"] = openalex.index(year=pillar["year"], use_cache=use_cache)
    print(f"  · {len(buckets['AAAI'])} papers")

    return buckets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-cache", action="store_true", help="re-hit the network")
    args = ap.parse_args()
    use_cache = not args.no_cache
    if not use_cache:
        http.RAW_DIR = http.RAW_DIR  # cache stays on disk, entries are overwritten

    buckets = fetch_all(use_cache=use_cache)

    os.makedirs(DATA, exist_ok=True)
    stats = {}
    for key, rows in buckets.items():
        with_abs = sum(1 for r in rows if r["abstract"])
        dup = len(rows) - len({r["title"].lower() for r in rows})
        stats[key] = {
            "papers": len(rows),
            "with_abstract": with_abs,
            "abstract_coverage": round(with_abs / len(rows), 4) if rows else 0,
            "duplicate_titles": dup,
            "with_doi": sum(1 for r in rows if r["doi"]),
            "with_pdf": sum(1 for r in rows if r["pdf_url"]),
            "with_authors": sum(1 for r in rows if r["authors"]),
        }
        print(f"{key:5s} papers={stats[key]['papers']:5d} "
              f"abstract={stats[key]['abstract_coverage']*100:5.1f}% "
              f"doi={stats[key]['with_doi']} dup_titles={dup}")

    out = {"stats": stats, "papers": {k: v for k, v in buckets.items()}}
    path = os.path.join(DATA, "corpus.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print(f"\nwrote {path} ({os.path.getsize(path)/1e6:.1f} MB)")

    meta = {"stats": stats, "pillars": PILLARS}
    mpath = os.path.join(DATA, "corpus_meta.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    print(f"wrote {mpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
