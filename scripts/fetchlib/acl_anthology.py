"""ACL Anthology adapter -- authoritative source for ACL proceedings.

Volume listing (MODS collection, one request per volume):
    https://aclanthology.org/volumes/2026.acl-long.xml
Paper page (the MODS record has no <abstract>, so the official abstract is read
from the rendered page):
    https://aclanthology.org/2026.acl-long.1/
"""
from __future__ import annotations

import html as _html
import re
import xml.etree.ElementTree as ET

from . import http
from .schema import clean, make_record

BASE = "https://aclanthology.org"
NS = {"m": "http://www.loc.gov/mods/v3"}
YEAR = 2026

# main-conference volumes; probed with HTTP so a missing volume never breaks the run
CANDIDATE_VOLUMES = [
    f"{YEAR}.acl-long",
    f"{YEAR}.acl-short",
    f"{YEAR}.acl-srw",
    f"{YEAR}.acl-demo",
    f"{YEAR}.acl-industry",
    f"{YEAR}.findings-acl",
]

_ID_RE = re.compile(r'href="/volumes/([^"]+)/?"')


def discover_volumes() -> list[str]:
    """Return volume ids actually present under the ACL <YEAR> event page."""
    page = http.get(f"{BASE}/events/acl-{YEAR}/", tag=f"acl_event_{YEAR}")
    found = [v for v in _ID_RE.findall(page) if v.startswith(str(YEAR))]
    ordered = sorted(set(found))
    return ordered or [v for v in CANDIDATE_VOLUMES if volume_exists(v)]


def volume_exists(volume_id: str) -> bool:
    try:
        http.get(f"{BASE}/volumes/{volume_id}.xml", tag="acl_volume_probe")
        return True
    except Exception:  # noqa: BLE001 - 404 etc. means "no such volume"
        return False


def _text(node, path: str) -> str:
    el = node.find(path, NS)
    return clean(el.text) if el is not None and el.text else ""


def _authors(node) -> list[str]:
    out = []
    for name in node.findall("m:name", NS):
        if name.get("type") not in (None, "personal"):
            continue
        given = _text(name, 'm:namePart[@type="given"]')
        family = _text(name, 'm:namePart[@type="family"]')
        full = f"{given} {family}".strip() or clean(
            "".join(name.itertext())).strip()
        if full and full not in out:
            out.append(full)
    return out


def _identifiers(node) -> dict:
    out = {}
    for el in node.findall("m:identifier", NS):
        out[el.get("type") or ""] = clean(el.text)
    return out


def _pages(node) -> str:
    part = node.find("m:part/m:extent", NS)
    if part is None:
        return ""
    start = _text(part, "m:start")
    end = _text(part, "m:end")
    return f"{start}-{end}" if start and end else ""


def index(volume_ids: list[str] | None = None, use_cache: bool = True) -> list[dict]:
    records: list[dict] = []
    for vol in (volume_ids or discover_volumes()):
        url = f"{BASE}/volumes/{vol}.xml"
        try:
            xml = http.get(url, tag=f"acl_volume_{vol}", use_cache=use_cache)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! volume {vol} unavailable: {exc}")
            continue
        root = ET.fromstring(xml.encode("utf-8"))
        for mods in root.findall("m:mods", NS):
            title = _text(mods, "m:titleInfo/m:title")
            citekey = mods.get("ID") or ""
            ids = _identifiers(mods)
            if not title or not ids.get("doi"):
                continue  # front matter / cover pages carry no DOI
            anum = re.search(r"\.([a-z0-9-]+)\.(\d+)$", ids["doi"].split("/")[-1])
            url_slug = ids["doi"].split("v1/")[-1] if "v1/" in ids["doi"] else citekey
            records.append(make_record(
                venue="ACL",
                year=YEAR,
                title=title,
                authors=_authors(mods),
                source="ACL Anthology",
                landing_url=f"{BASE}/{url_slug}/",
                pdf_url=f"{BASE}/{url_slug}.pdf",
                doi=ids["doi"],
                pages=_pages(mods),
                extra={
                    "paper_id": f"acl-{url_slug}",
                    "volume": vol,
                    "citekey": citekey,
                    "paper_xml_url": f"{BASE}/{url_slug}.xml",
                    "track": (anum.group(1) if anum else vol),
                },
            ))
    return records


_ABS_START = 'card-body acl-abstract">'
_ABS_END_MARKS = ("<dt>Anthology ID", "</div></div><dl>", "</div></div>")
_TITLE_BLOCK = re.compile(r'<h4[^>]*id="Title"[^>]*>(.*?)</h4>', re.S)


def _paper_page(landing_url: str, use_cache: bool = True) -> str:
    # strict utf-8: the Anthology serves multibyte math in abstracts
    return http.get(landing_url, tag="acl_page", use_cache=use_cache)


def abstract(landing_url: str, use_cache: bool = True) -> str:
    """Official abstract as rendered by the ACL Anthology paper page.

    The Anthology nests <span class=tex-math> inside the abstract, so a lazy
    </span> match truncates it; slice down to the metadata list instead.
    """
    page = _paper_page(landing_url, use_cache)
    i = page.find(_ABS_START)
    if i < 0:
        return ""
    body = page[i + len(_ABS_START):]
    cut = len(body)
    for mark in _ABS_END_MARKS:
        j = body.find(mark)
        if 0 <= j < cut:
            cut = j
    body = body[:cut]
    body = re.sub(r"<h5[^>]*>.*?</h5>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return clean(_html.unescape(body))


def official_title(landing_url: str, use_cache: bool = True) -> str:
    page = _paper_page(landing_url, use_cache)
    m = _TITLE_BLOCK.search(page)
    if not m:
        return ""
    return clean(_html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))))
