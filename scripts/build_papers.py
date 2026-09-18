#!/usr/bin/env python3
"""Resolve data/selection.json into fully-populated records.

  python scripts/build_papers.py --draft    # write data/draft.json (EN abstracts to translate)
  python scripts/build_papers.py            # merge data/translations.json -> data/papers.json
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetchlib import acl_anthology, cvf, http, openalex  # noqa: E402
from pillars import BY_KEY, PILLARS  # noqa: E402
from topics import BY_ID, TOPICS, UMBRELLA, match_topics  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

STOP = set("""a an the of for and or with on in to via from by is are as that this these those
its it we our their they which when where what how why can not no all more most other some
such between into over under about toward towards using used use new novel based learning method
methods approach approaches framework model models data task tasks tasks. study paper propose
proposed results experiment experiments benchmark benchmarks problem problems performance
highly effective general efficient simple unified large scale cross multi end state art
two three several both each also been will would may might must than then there here
""".split())


def keyword_candidates(title: str, abstract: str, limit: int = 14) -> list[str]:
    """Real terms only: frequency-ranked noun-ish tokens + salient capitalised phrases."""
    text = f"{title}. {abstract}"
    words = re.findall(r"[A-Za-z][A-Za-z\-']{2,}", text)
    counts: collections.Counter = collections.Counter()
    for w in words:
        lw = w.lower()
        if lw in STOP or len(lw) < 4:
            continue
        counts[lw] += 1
    caps = re.findall(r"\b(?:[A-Z][a-z0-9\-]*\s){1,3}[A-Z][a-z0-9\-]*\b", title)
    caps += re.findall(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)?\b", text)
    phrases = []
    for c in caps:
        c = re.sub(r"\s+", " ", c).strip()
        if len(c) > 3 and c.lower() not in STOP and c not in phrases:
            phrases.append(c)
    out = [p for p in phrases[:6]]
    for w, n in counts.most_common():
        if w not in [o.lower() for o in out]:
            out.append(w)
        if len(out) >= limit:
            break
    return out[:limit]


def find_citations(rec: dict) -> dict:
    """OpenAlex lookup by DOI, else exact-title match. Absent stays absent."""
    doi = (rec.get("doi") or "").strip()
    try:
        if doi:
            url = (f"{openalex.API}/works?filter="
                   + urllib.parse.quote(f"doi:{doi}")
                   + f"&select=id,cited_by_count,title&mailto={openalex.MAILTO}")
        else:
            url = (f"{openalex.API}/works?filter="
                   + urllib.parse.quote(f"title.search:{rec['title']}")
                   + f"&select=id,cited_by_count,title&mailto={openalex.MAILTO}")
        payload = http.get_json(url, tag="openalex_cite", use_cache=True)
    except Exception:  # noqa: BLE001 - citations are optional metadata
        return {"citations": None, "citations_source": None}
    def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
    for w in payload.get("results", [])[:5]:
        if norm(w.get("title")) == norm(rec["title"]):
            return {"citations": w.get("cited_by_count"),
                    "citations_source": "OpenAlex " + (w.get("id") or "").split("/")[-1]}
    return {"citations": None, "citations_source": None}


def official_abstract(rec: dict, use_cache: bool = True) -> tuple[str, str]:
    venue = rec["venue"]
    try:
        if venue in ("CVPR", "ICCV"):
            return cvf.abstract(rec["landing_url"], use_cache), "CVF Open Access 论文页"
        if venue == "ACL":
            return acl_anthology.abstract(rec["landing_url"], use_cache), "ACL Anthology 论文页"
    except Exception as exc:  # noqa: BLE001
        print(f"  ! abstract failed {rec['paper_id']}: {exc}")
    return rec.get("abstract") or "", rec["provenance"]["source"]


def _draft_is_fresh(draft_path: str) -> bool:
    """The draft caches resolved records, so any change that alters record shape
    (this script, the selection list, the corpus) must invalidate it."""
    try:
        made = os.path.getmtime(draft_path)
    except OSError:
        return False
    for dep in (__file__, os.path.join(DATA, "selection.json"),
                os.path.join(DATA, "corpus.json")):
        if os.path.exists(dep) and os.path.getmtime(dep) > made:
            print(f"  · draft 早于 {os.path.basename(dep)}，重新回源")
            return False
    return True


def resolve(use_cache: bool = True) -> list[dict]:
    corpus = json.load(open(os.path.join(DATA, "corpus.json"), encoding="utf-8"))
    sel = json.load(open(os.path.join(DATA, "selection.json"), encoding="utf-8"))
    by_ref = {}
    for venue, rows in corpus["papers"].items():
        for r in rows:
            by_ref[r["paper_id"]] = r

    out = []
    for i, pick in enumerate(sel["papers"], start=1):
        rec = by_ref.get(pick["ref"])
        if rec is None:
            print(f"  ! unresolved ref {pick['ref']}")
            continue
        if rec["venue"] == "AAAI":
            # OpenAlex holds the AAAI record; on refresh re-query by DOI so an
            # upstream correction is picked up instead of frozen in corpus.json.
            abs_text = rec["abstract"]
            if not use_cache:
                abs_text = (openalex.abstract_by_doi(rec.get("doi") or "")
                            or rec["abstract"])
            abs_src = rec["provenance"]["source"]
        else:
            abs_text, abs_src = official_abstract(rec, use_cache)
        if not abs_text:
            print(f"  ! no official abstract for {pick['ref']} -> dropped")
            continue
        blob = f"{rec['title']} . {abs_text}"
        rule_topics = match_topics(blob, max_topics=3)
        primary = pick["primary_topic"]
        topics = [primary] + [t for t in rule_topics if t != primary]
        out.append({
            "id": f"{rec['venue'].lower()}-{i:03d}-{rec['paper_id']}",
            "venue": rec["venue"],
            "year": rec["year"],
            "title": rec["title"],
            "authors": rec["authors"],
            "abstract": abs_text,
            "keywords_en_auto": keyword_candidates(rec["title"], abs_text),
            "topics": topics[:3],
            "primary_topic": primary,
            "topic_rule_agree": primary in rule_topics,
            "curator_note": pick.get("rationale", ""),
            "links": {
                # AAAI: official page is the DOI landing (ojs.aaai.org); OpenAlex id
                # is only the record we read it from, so expose it as a second link.
                "official": rec.get("publisher_url") or rec["landing_url"],
                "pdf": (rec.get("pdf_url") or "")
                       if (rec.get("pdf_url") or "") != (rec.get("publisher_url") or rec["landing_url"])
                       else "",   # OA url that is just the landing page isn't a PDF
                "doi": rec.get("doi") or "",
                "extra": rec.get("supp_url") or rec.get("code_url") or "",
                "record": (rec["landing_url"] if rec.get("publisher_url") else ""),
            },
            "pages": rec.get("pages") or "",
            "track": rec.get("volume") or "",
            "provenance": {
                "source": rec["provenance"]["source"],
                "abstract_source": abs_src,
                "retrieved_at": rec["provenance"]["retrieved_at"],
                "paper_id": rec["paper_id"],
            },
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--citations", action="store_true", help="extra OpenAlex lookups")
    ap.add_argument("--force-refetch", action="store_true", help="ignore data/draft.json cache")
    args = ap.parse_args()

    draft_path = os.path.join(DATA, "draft.json")
    if not args.draft and os.path.exists(draft_path) and not args.force_refetch \
            and _draft_is_fresh(draft_path):
        # draft.json already carries the official abstracts + OpenAlex citation counts
        papers = json.load(open(draft_path, encoding="utf-8"))
        print(f"reuse {draft_path} ({len(papers)} papers; --force-refetch 可重新回源)")
    else:
        papers = resolve()
    if args.citations or (papers and papers[0].get("citations") is None
                          and "citations" not in papers[0]):
        for p in papers:
            p.update(find_citations(p))
            print(f"  · {p['venue']:4s} cites={p.get('citations')} {p['title'][:48]}")
    if args.draft:
        path = os.path.join(DATA, "draft.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(papers, fh, ensure_ascii=False, indent=2)
        print(f"wrote {path} — {len(papers)} papers")
        disagree = [p["id"] for p in papers if not p["topic_rule_agree"]]
        if disagree:
            print("策展主题与规则不一致（需复核）:", ", ".join(disagree))
        return 0

    tdir = os.path.join(DATA, "translations")
    if not os.path.isdir(tdir):
        print("缺 data/translations/（人工中文翻译目录），先跑 --draft")
        return 1
    tmap = {}
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".json"):
            continue
        blob = json.load(open(os.path.join(tdir, fn), encoding="utf-8"))
        for t in blob["papers"]:
            tmap[t["id"]] = t
        print(f"  + {fn}: {len(blob['papers'])} 篇译文")
    missing = []
    for i, p in enumerate(papers, start=1):
        t = tmap.get(p["id"])
        if not t:
            missing.append(p["id"])
            continue
        p["title_zh"] = t["title_zh"]
        p["abstract_zh"] = t["abstract_zh"]
        p["keywords"] = t["keywords"]           # [{en, zh}]
        p["topics"] = t.get("topics", p["topics"])
        p["rank"] = i
    if missing:
        print("未翻译，终止：", ", ".join(missing))
        return 1

    by_venue = collections.Counter(p["venue"] for p in papers)
    by_topic = collections.Counter(t for p in papers for t in p["topics"])
    cmeta = os.path.join(DATA, "corpus_meta.json")
    corpus_stats = json.load(open(cmeta, encoding="utf-8"))["stats"] if os.path.exists(cmeta) else {}
    meta = {
        "schema_version": 1,
        "generated_at": http.time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pillars": PILLARS,
        "corpus": corpus_stats,
        "corpus_total": sum(s.get("papers", 0) for s in corpus_stats.values()),
        "topics": [{k: t[k] for k in ("id", "label", "label_en", "accent")} for t in TOPICS],
        "umbrella": UMBRELLA,
        "counts": {"papers": len(papers), "by_venue": dict(by_venue),
                   "by_topic": dict(by_topic)},
        "translation": {
            "mode": "人工翻译（逐篇，非机翻）",
            "translator": "Qoder agent，逐篇对照官方英文摘要翻译",
            "verified_against": "官方摘要页 / OpenAlex 收录的官方记录",
        },
        "topic_disclaimer": "主题标签由本项目按官方标题与摘要派生，不是出版方学科分类。",
    }
    out = {"meta": meta, "papers": papers,
           "pillars": PILLARS,
           "topics": meta["topics"], "umbrella": UMBRELLA,
           "topic_disclaimer": meta["topic_disclaimer"]}
    path = os.path.join(DATA, "papers.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"wrote {path} — {len(papers)} papers, venues={dict(by_venue)}")
    print("topic counts:", dict(by_topic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
