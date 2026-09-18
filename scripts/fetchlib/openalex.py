"""OpenAlex adapter -- used for AAAI (CVF/Anthology have no API coverage there).

Proceedings of the AAAI Conference on Artificial Intelligence = source S4210191458.
Abstracts arrive as an inverted index and are reassembled here.
"""
from __future__ import annotations

from . import http
from .schema import clean, make_record

API = "https://api.openalex.org"
MAILTO = "researcher@example.org"
AAAI_SOURCE = "S4210191458"

FIELDS = ("id,doi,title,publication_year,authorships,primary_location,"
          "abstract_inverted_index,open_access,ids,cited_by_count,concepts")


def _restore(inverted: dict | None) -> str:
    if not inverted:
        return ""
    pos: dict[int, str] = {}
    for word, idxs in inverted.items():
        for i in idxs:
            pos[i] = word
    return clean(" ".join(pos[i] for i in sorted(pos)))


def works(source: str = AAAI_SOURCE, year: int = 2026,
          per_page: int = 200, use_cache: bool = True) -> list[dict]:
    rows: list[dict] = []
    cursor = "*"
    page_no = 0
    while cursor:
        page_no += 1
        url = (f"{API}/works?filter=primary_location.source.id:{source},"
               f"publication_year:{year}"
               f"&per-page={per_page}&cursor={cursor}&select={FIELDS}"
               f"&mailto={MAILTO}")
        payload = http.get_json(url, tag=f"openalex_{source}_{year}_p{page_no}",
                                use_cache=use_cache)
        batch = payload.get("results", [])
        rows.extend(batch)
        meta = payload.get("meta", {})
        cursor = meta.get("next_cursor") or ""
        total = meta.get("count", 0)
        print(f"  · openalex page {page_no}: +{len(batch)} (total {total})")
        if not batch or len(rows) >= total:
            break
    return rows


def _best_pdf(work: dict) -> str:
    oa = work.get("open_access") or {}
    url = oa.get("oa_url") or ""
    return url if url.startswith("http") else ""


def index(year: int = 2026, use_cache: bool = True) -> list[dict]:
    records: list[dict] = []
    for i, w in enumerate(works(year=year, use_cache=use_cache), start=1):
        title = clean(w.get("title"))
        if not title:
            continue
        authors = [clean((a.get("author") or {}).get("display_name"))
                   for a in (w.get("authorships") or [])]
        loc = (w.get("primary_location") or {})
        src = (loc.get("source") or {})
        doi = clean(w.get("doi") or "").replace("https://doi.org/", "")
        concepts = [clean(c.get("display_name"))
                    for c in (w.get("concepts") or []) if c.get("score")]
        records.append(make_record(
            venue="AAAI",
            year=int(w.get("publication_year") or year),
            title=title,
            authors=[a for a in authors if a],
            abstract=_restore(w.get("abstract_inverted_index")),
            source="OpenAlex",
            landing_url=clean(w.get("id") or ""),
            pdf_url=_best_pdf(w),
            doi=doi,
            extra={
                "paper_id": f"aaai-{year}-w{i}",
                "openalex_id": clean((w.get("id") or "").split("/")[-1]),
                "cited_by_count": w.get("cited_by_count") or 0,
                "publisher": clean(src.get("display_name")),
                "oa_url": _best_pdf(w),
                "landing_url_openalex": clean(w.get("id") or ""),
                "publisher_url": (f"https://doi.org/{doi}" if doi else ""),
                # publisher-side subject tags: real signals for keyword extraction
                "concepts": [c for c in concepts if c][:12],
                "n_authors": len([a for a in authors if a]),
            },
        ))
    return records


def abstract_by_doi(doi: str, use_cache: bool = False) -> str:
    """Fresh single-record read: used when refreshing AAAI metadata."""
    if not doi:
        return ""
    import urllib.parse
    q = urllib.parse.urlencode({
        "filter": f"doi:{doi}", "select": "abstract_inverted_index",
        "mailto": MAILTO,
    })
    try:
        payload = http.get_json(f"{API}/works?{q}", tag="openalex_one",
                                use_cache=use_cache)
    except Exception:  # noqa: BLE001
        return ""
    for w in payload.get("results", []):
        text = _restore(w.get("abstract_inverted_index"))
        if text:
            return text
    return ""


def concepts_for(title: str, limit: int = 5) -> list[str]:
    """Cross-check helper: ask OpenAlex what a titled work is about."""
    import urllib.parse
    q = urllib.parse.urlencode({
        "search": title, "per-page": limit, "select": "title,concepts",
        "mailto": MAILTO,
    })
    payload = http.get_json(f"{API}/works?{q}", tag="openalex_concepts")
    out: list[str] = []
    for w in payload.get("results", []):
        for c in (w.get("concepts") or [])[:6]:
            name = clean(c.get("display_name"))
            if name and name not in out:
                out.append(name)
    return out
