"""Normalized record helpers shared by every fetcher."""
from __future__ import annotations

import re
import time
import unicodedata

WS = re.compile(r"\s+")


def clean(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r", "\n")
    return WS.sub(" ", text).strip()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def make_record(*, venue: str, year: int, title: str, authors: list[str],
                source: str, landing_url: str, pdf_url: str = "",
                abstract: str = "", doi: str = "", pages: str = "",
                extra: dict | None = None) -> dict:
    rec = {
        "venue": venue,
        "year": year,
        "title": clean(title),
        "authors": [clean(a) for a in authors if clean(a)],
        "abstract": clean(abstract),
        "landing_url": landing_url,
        "pdf_url": pdf_url,
        "doi": doi,
        "pages": clean(pages),
        # provenance: which official system produced this record and when.
        "provenance": {
            "source": source,
            "retrieved_at": now_iso(),
            "verified": bool(clean(abstract)),
        },
    }
    if extra:
        rec.update(extra)
    return rec


def slugify(text: str, limit: int = 60) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:limit]
