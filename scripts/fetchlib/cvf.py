"""CVF Open Access adapter -- authoritative source for CVPR / ICCV.

Index page (one request, full proceedings):
    https://openaccess.thecvf.com/CVPR2026?day=all
Each paper page carries the publisher abstract:
    https://openaccess.thecvf.com/content/CVPR2026/html/<file>_paper.html
"""
from __future__ import annotations

import html
import re

from . import http
from .schema import clean, make_record

BASE = "https://openaccess.thecvf.com"

# user asked for "CUPR" -> confirmed as CVPR; ICCV is odd-year so 2025 is its latest edition
VENUES = {
    "CVPR": {"code": "CVPR2026", "year": 2026, "label": "CVPR 2026"},
    "ICCV": {"code": "ICCV2025", "year": 2025, "label": "ICCV 2025"},
}

_PTITLE = re.compile(r'<dt class="ptitle">\s*<br>\s*<a href="([^"]+)">(.*?)</a>\s*</dt>', re.S)
_AUTHOR = re.compile(r'name="query_author" value="([^"]*)"')
_PDF = re.compile(r'href="(/content/[^"]+?_paper\.pdf)"')
_SUPP = re.compile(r'href="(/content/[^"]+?supplemental[^"]*?\.pdf)"')
_CODE = re.compile(r'href="(/content/[^"]+?(?:code|data)[^"]*?\.zip)"')
_BIB_PAGES = re.compile(r'pages\s*=\s*\{([^}]*)\}')
_BIB_YEAR = re.compile(r'year\s*=\s*\{(\d{4})\}')
# CVF prints the official citation entry right in the proceedings index page
_BIBTEX = re.compile(r'<div class="bibref pre-white-space">(@InProceedings\{.*?\n\})', re.S)
_ABSTRACT = re.compile(r'<div id="abstract"[^>]*>(.*?)</div>', re.S)
_COPYRIGHT = re.compile(r'<div id="abstract"[^>]*>.*?</div>', re.S)


def index(venue_key: str, use_cache: bool = True) -> list[dict]:
    """Return the full paper listing for one CVF proceedings volume."""
    meta = VENUES[venue_key]
    url = f"{BASE}/{meta['code']}?day=all"
    page = http.get(url, tag=f"cvf_index_{meta['code']}", use_cache=use_cache)

    marks = list(_PTITLE.finditer(page))
    records: list[dict] = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(page)
        block = page[start:end]

        landing = http.join(BASE + "/", m.group(1))
        title = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))

        authors: list[str] = []
        for a in _AUTHOR.findall(block):
            a = html.unescape(a)
            if not authors or authors[-1] != a:
                authors.append(a)

        pdf = _PDF.search(block)
        supp = _SUPP.search(block)
        code = _CODE.search(block)
        pages = _BIB_PAGES.search(block)
        year_m = _BIB_YEAR.search(block)
        bib = _BIBTEX.search(block)

        records.append(make_record(
            venue=venue_key,
            year=int(year_m.group(1)) if year_m else meta["year"],
            title=html.unescape(title),
            authors=authors,
            source="CVF Open Access",
            landing_url=landing,
            pdf_url=(BASE + pdf.group(1)) if pdf else "",
            pages=pages.group(1) if pages else "",
            extra={
                "paper_id": f"{meta['code']}-p{len(records) + 1}",
                "abstract_url": landing,
                "supp_url": (BASE + supp.group(1)) if supp else "",
                "code_url": (BASE + code.group(1)) if code else "",
                # verbatim official citation entry
                "bibtex": html.unescape(bib.group(1)).strip() if bib else "",
            },
        ))
    return records


def abstract(landing_url: str, use_cache: bool = True) -> str:
    """Fetch and return the publisher abstract from a CVF paper page."""
    page = http.get(landing_url, tag="cvf_paper", use_cache=use_cache)
    m = _ABSTRACT.search(page)
    if not m:
        return ""
    raw = re.sub(r"<[^>]+>", " ", m.group(1))
    raw = html.unescape(raw)
    # CVF puts a "IEEE Conference on Computer Vision..." line after the abstract
    raw = re.split(r'These CVPR|These ICCV|These [A-Z]+\S* proceedings', raw)[0]
    return clean(raw)


def abstract_meta(landing_url: str, use_cache: bool = True) -> dict:
    page = http.get(landing_url, tag="cvf_paper", use_cache=use_cache)
    out = {}
    m = re.search(r'<div id="papertitle">(.*?)</div>', page, re.S)
    if m:
        out["official_title"] = clean(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))))
    m = re.search(r'\[.*?pp\.\s*([\d-]+)', page, re.S)
    if m:
        out["official_pages"] = m.group(1)
    return out
