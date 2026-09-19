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
from pillars import EDITIONS, PILLARS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def fetch_all(use_cache: bool = True) -> dict:
    """Fetch every edition in pillars.EDITIONS, merged into four venue buckets."""
    buckets: dict[str, list] = {p["key"]: [] for p in PILLARS}

    for ed in EDITIONS:
        venue, year = ed["venue"], ed["year"]
        if ed["kind"] == "cvf":
            print(f"[CVF] {ed['label']} …")
            rows = cvf.index(venue, year, use_cache=use_cache)
        elif ed["kind"] == "acl":
            print(f"[ACL] {ed['label']} volumes …")
            vols = acl_anthology.discover_volumes(year)
            print(f"  · {', '.join(vols)}")
            rows = acl_anthology.index(year, vols, use_cache=use_cache)
        else:
            print(f"[OpenAlex] {ed['label']} …")
            rows = openalex.index(year=year, use_cache=use_cache)
        print(f"  · {len(rows)} papers")
        buckets[venue].extend(rows)

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
    for ed in EDITIONS:
        rows = [r for r in buckets[ed["venue"]] if r["year"] == ed["year"]]
        with_abs = sum(1 for r in rows if r["abstract"])
        stats[ed["label"]] = {
            "venue": ed["venue"], "year": ed["year"], "papers": len(rows),
            "with_abstract": with_abs,
            "abstract_coverage": round(with_abs / len(rows), 4) if rows else 0,
            "duplicate_titles": len(rows) - len({r["title"].lower() for r in rows}),
            "with_doi": sum(1 for r in rows if r["doi"]),
            "with_pdf": sum(1 for r in rows if r["pdf_url"]),
            "with_bibtex": sum(1 for r in rows if r.get("bibtex")),
        }
        s = stats[ed["label"]]
        print(f"{ed['label']:11s} papers={s['papers']:5d} abstract={s['abstract_coverage']*100:5.1f}% "
              f"doi={s['with_doi']:5d} pdf={s['with_pdf']:5d} bib={s['with_bibtex']:5d} dup={s['duplicate_titles']}")

    out = {"stats": stats, "papers": {k: v for k, v in buckets.items()}}
    path = os.path.join(DATA, "corpus.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    total = sum(s["papers"] for s in stats.values())
    print(f"\nwrote {path} ({os.path.getsize(path)/1e6:.1f} MB, {total} papers)")

    meta = {"stats": stats, "pillars": PILLARS, "editions": EDITIONS, "total": total}
    mpath = os.path.join(DATA, "corpus_meta.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    print(f"wrote {mpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
