"""Citation formats.

BibTeX is the *official* text whenever a publisher gives it:
  CVPR/ICCV  -> embedded verbatim in the CVF proceedings index (corpus field `bibtex`)
  ACL        -> https://aclanthology.org/<id>.bib (Anthology's own export)
  AAAI       -> DOI content negotiation with Crossref (`Accept: application/x-bibtex`)
RIS and Markdown are rendered from our already-verified structured fields, and
`provenance` in the export says which of the two it is.
"""
from __future__ import annotations

import urllib.parse
import urllib.request

from . import http

_CITEKEY_FALLBACK = {"CVPR": "cvpr2026", "ICCV": "iccv2025", "AAAI": "aaai2026", "ACL": "acl2026"}


def _doi_bibtex(doi: str) -> str:
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/x-bibtex; charset=utf-8",
        "User-Agent": http.USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.read().decode("utf-8", "replace").strip()
    except Exception:  # noqa: BLE001 - caller falls back to rendered entry
        return ""


def _acl_bib(landing_url: str) -> str:
    url = landing_url.rstrip("/") + ".bib"
    try:
        return http.get(url, tag="acl_bib").strip()
    except Exception:  # noqa: BLE001
        return ""


def bibtex_for(paper: dict) -> tuple[str, str]:
    """Return (bibtex text, origin label). Empty text means 'render it instead'."""
    venue = paper["venue"]
    if venue in ("CVPR", "ICCV"):
        raw = (paper.get("bibtex") or "").strip()
        return (raw, "CVF Open Access 目录内嵌官方 BibTeX") if raw else ("", "")
    if venue == "ACL":
        raw = _acl_bib(paper["links"]["official"])
        return (raw, "ACL Anthology 官方 .bib 导出") if raw else ("", "")
    if venue == "AAAI" and paper["links"].get("doi"):
        raw = _doi_bibtex(paper["links"]["doi"])
        return (raw, "Crossref（经 AAAI DOI 内容协商）") if raw else ("", "")
    return ("", "")


def citekey(paper: dict) -> str:
    first = (paper["authors"] or [{}])[0] if paper.get("authors") else ""
    surname = (first.split()[-1] if first else "anon").lower()
    return f"{surname}{paper['year']}{paper['title'].split(':')[0].split()[0].lower().strip(',()')[:14]}"


def rendered_bibtex(paper: dict) -> str:
    """Fallback entry built from verified fields, marked as such by the caller."""
    kind = "article" if paper["venue"] == "AAAI" else "inproceedings"
    f = {
        "author": " and ".join(paper["authors"]),
        "title": paper["title"],
        "year": str(paper["year"]),
    }
    if kind == "article":
        f.update({"journal": paper.get("venue_full") or "Proceedings of the AAAI Conference on Artificial Intelligence",
                  "publisher": "AAAI"})
    else:
        f["booktitle"] = paper.get("venue_full") or paper["venue"]
    if paper.get("pages"):
        f["pages"] = paper["pages"]
    if paper["links"].get("doi"):
        f["doi"] = paper["links"]["doi"]
    f["url"] = paper["links"]["official"]
    body = "\n".join(f"  {k:<10} = {{{v}}}," for k, v in f.items())
    return "@%s{%s,\n%s\n}" % (kind, citekey(paper), body.rstrip(","))


def to_ris(paper: dict) -> str:
    t = "JOUR" if paper["venue"] == "AAAI" else "CPRO"
    lines = [f"TY  - {t}", f"TI  - {paper['title']}"]
    lines += [f"AU  - {a}" for a in paper["authors"]]
    lines.append(f"PY  - {paper['year']}")
    lines.append(f"BT  - {paper.get('venue_full') or paper['venue']}")
    if paper.get("pages"):
        pp = paper["pages"].split("-")
        lines.append(f"SP  - {pp[0]}")
        if len(pp) > 1:
            lines.append(f"EP  - {pp[1]}")
    if paper["links"].get("doi"):
        lines.append(f"DO  - {paper['links']['doi']}")
    lines.append(f"UR  - {paper['links']['official']}")
    if paper["links"].get("pdf"):
        lines.append(f"L1  - {paper['links']['pdf']}")
    lines.append("ER  - ")
    return "\n".join(lines)


def to_markdown(paper: dict) -> str:
    authors = ", ".join(paper["authors"][:8]) + (" 等" if len(paper["authors"]) > 8 else "")
    pages = f", pp. {paper['pages']}" if paper.get("pages") else ""
    doi = f". DOI: [{paper['links']['doi']}](https://doi.org/{paper['links']['doi']})" \
        if paper["links"].get("doi") else ""
    return (f"- {authors} ({paper['year']}). **{paper['title']}**. "
            f"{paper.get('venue_full') or paper['venue']}{pages}{doi}. "
            f"[论文页]({paper['links']['official']})")


def render_bundle(papers: list[dict], fmt: str) -> tuple[str, str]:
    """Return (text, media_type)."""
    if fmt == "bib":
        blocks, official = [], 0
        for p in papers:
            raw, origin = bibtex_for(p)
            if raw:
                official += 1
                blocks.append(f"% {origin}\n{raw}")
            else:
                blocks.append("% 由本项目已核验字段渲染（官方未提供 BibTeX 条目）\n"
                              + rendered_bibtex(p))
        head = (f"% 顶会四支柱看板导出｜{len(papers)} 篇｜"
                f"其中 {official} 篇为出版方官方 BibTeX 原文，其余 {len(papers) - official} 篇由已核验字段渲染\n\n")
        return head + "\n\n".join(blocks) + "\n", "application/x-bibtex; charset=utf-8"
    if fmt == "ris":
        return "\n\n".join(to_ris(p) for p in papers) + "\n", \
            "application/x-research-info-systems; charset=utf-8"
    if fmt == "md":
        lines = [f"# 顶会四支柱看板 · 引用表（{len(papers)} 篇）", "",
                 "作者、标题、页码、DOI 与链接均取自会议官方开放获取记录。", ""]
        cur = None
        for p in sorted(papers, key=lambda x: (x["venue"], x["rank"])):
            if p["venue"] != cur:
                cur = p["venue"]
                lines += [f"## {p['venue']} {p['year']}", ""]
            lines.append(to_markdown(p))
        return "\n".join(lines) + "\n", "text/markdown; charset=utf-8"
    raise ValueError(fmt)
