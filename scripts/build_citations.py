#!/usr/bin/env python3
"""Resolve each curated paper's citation and write the downloadable bundles.

  data/citations.json      {id: {text, origin, official}}   (cached, re-run is offline)
  web/data/export/*.{bib,ris,md}   all + one file per pillar
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EXPORT = os.path.join(ROOT, "web", "data", "export")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from fetchlib import citation  # noqa: E402


def load_papers() -> list[dict]:
    with open(os.path.join(DATA, "papers.json"), encoding="utf-8") as fh:
        return json.load(fh)["papers"]


def resolve(papers: list[dict], cache_path: str, force: bool) -> dict:
    cache = {}
    if os.path.exists(cache_path) and not force:
        with open(cache_path, encoding="utf-8") as fh:
            cache = json.load(fh)
    for p in papers:
        if not force and p["id"] in cache and cache[p["id"]].get("text"):
            continue
        text, origin = citation.bibtex_for(p)
        if not text:
            text, origin = citation.rendered_bibtex(p), "本项目按已核验字段渲染"
        cache[p["id"]] = {"text": text, "origin": origin,
                          "official": not origin.startswith("本项目")}
        print(f"  · {p['venue']:4s} {'官方' if not origin.startswith('本项目') else '渲染'} "
              f"{origin[:34]:36s} {p['title'][:36]}")
    with open(cache_path, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=2)
    return cache


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-resolve (re-hits ACL/Crossref)")
    args = ap.parse_args()

    papers = load_papers()
    cpath = os.path.join(DATA, "citations.json")
    cache = resolve(papers, cpath, args.force)

    # single owner of the `citation` field: fold it back into papers.json so the
    # modal can copy a citation offline, with no network call at view time
    pj = os.path.join(DATA, "papers.json")
    changed = 0
    for p in papers:
        c = cache.get(p["id"])
        if c and p.get("citation") != c:
            p["citation"] = c
            changed += 1
    if changed:
        with open(os.path.join(ROOT, "data", "papers.json"), encoding="utf-8") as fh:
            blob = json.load(fh)
        blob["papers"] = papers
        blob["meta"]["citation"] = {
            "official_bibtex": sum(1 for v in cache.values() if v["official"]),
            "rendered": sum(1 for v in cache.values() if not v["official"]),
            "note": "BibTeX 优先取出版方原文（CVF 目录内嵌 / ACL 官方 .bib / AAAI 经 DOI 协商的 Crossref 条目）；"
                    "取不到时才由本项目已核验字段渲染，并在导出文件头部标注。",
        }
        with open(pj, "w", encoding="utf-8") as fh:
            json.dump(blob, fh, ensure_ascii=False, indent=2)
        print(f"merged citation into papers.json ({changed} 条)")

    os.makedirs(EXPORT, exist_ok=True)
    official = sum(1 for v in cache.values() if v["official"])
    print(f"citation 条目 {len(cache)}，其中出版方官方 BibTeX {official} 篇")

    # hard gate: no paper ships without a citation entry
    bad = [p["id"] for p in papers
           if not (cache.get(p["id"]) or {}).get("text", "").lstrip().startswith("@")]
    if bad:
        print("引用条目缺失或非 BibTeX：", ", ".join(bad))
        return 1

    groups = {"all": papers}
    for venue in ("CVPR", "AAAI", "ICCV", "ACL"):
        groups[venue] = [p for p in papers if p["venue"] == venue]

    manifest = {}
    for name, subset in groups.items():
        for fmt in ("bib", "ris", "md"):
            text, ctype = citation.render_bundle(subset, fmt)
            fn = f"{name.lower()}.{fmt}"
            with open(os.path.join(EXPORT, fn), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            manifest[fn] = {"format": fmt, "papers": len(subset), "bytes": len(text.encode())}
    with open(os.path.join(EXPORT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"generated_at": papers[0]["provenance"]["retrieved_at"],
                   "official_bibtex": official, "files": manifest},
                  fh, ensure_ascii=False, indent=2)
    print("wrote", os.path.relpath(EXPORT, ROOT), f"({len(manifest)} 个文件)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
