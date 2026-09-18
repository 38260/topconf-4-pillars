"""HTTP with on-disk cache, retry and polite rate limiting.

Only stdlib is used so the fetch pipeline runs anywhere Python 3.8+ exists.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")

USER_AGENT = (
    "topconf-4-pillars/1.0 (research dashboard; respects crawler etiquette; "
    "mailto:researcher@example.org)"
)

_min_interval = float(os.environ.get("FETCH_MIN_INTERVAL", "0.4"))
_last_hit = 0.0


def _throttle() -> None:
    global _last_hit
    wait = _min_interval - (time.time() - _last_hit)
    if wait > 0:
        time.sleep(wait)
    _last_hit = time.time()


def _cache_path(url: str, tag: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    name = tag + "_" + digest
    return os.path.join(RAW_DIR, name + ".bin")


def get(url: str, tag: str = "get", use_cache: bool = True,
        retries: int = 3, timeout: int = 60) -> str:
    """Fetch *url* as text. Responses are cached under data/raw/."""
    os.makedirs(RAW_DIR, exist_ok=True)
    path = _cache_path(url, tag)
    if use_cache and os.path.exists(path):
        with open(path, "rb") as fh:
            body = fh.read()
        return _decode(body, url)

    last_err: Exception | None = None
    for attempt in range(retries):
        _throttle()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = _inflate(resp.read(), resp.headers.get("Content-Encoding"))
                status = resp.status
            if status >= 400:
                raise urllib.error.HTTPError(url, status, "http error", None, None)
            with open(path, "wb") as fh:
                fh.write(body)
            _write_meta(url, tag, path, len(body))
            return _decode(body, url)
        except Exception as exc:  # noqa: BLE001 - retry then surface
            last_err = exc
            code = getattr(exc, "code", None)
            if code in (404, 400):
                break
            sleep_for = 1.5 * (2 ** attempt)
            if code == 429:
                sleep_for = max(sleep_for, 8.0)
            print(f"  ! {tag} retry {attempt + 1}/{retries} after {sleep_for:.1f}s: {exc}")
            time.sleep(sleep_for)
    raise RuntimeError(f"fetch failed: {url} ({last_err})")


def get_json(url: str, tag: str = "json", **kw):
    return json.loads(get(url, tag=tag, **kw))


def _inflate(raw: bytes, encoding: str | None) -> bytes:
    if not raw:
        return raw
    enc = (encoding or "").lower()
    try:
        if enc == "gzip" or raw[:2] == b"\x1f\x8b":
            return gzip.decompress(raw)
        if enc in ("deflate", "br") and enc == "deflate":
            return zlib.decompress(raw)
    except Exception:  # noqa: BLE001 - fall through to raw bytes
        try:
            return zlib.decompress(raw, -zlib.MAX_WBITS)
        except Exception:  # noqa: BLE001
            return raw
    return raw


def _decode(body: bytes, url: str) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return body.decode(enc)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")


def _write_meta(url: str, tag: str, path: str, size: int) -> None:
    meta = {
        "url": url,
        "tag": tag,
        "cached_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "bytes": size,
        "file": os.path.relpath(path, ROOT).replace("\\", "/"),
    }
    with open(path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)


def join(base: str, rel: str) -> str:
    return urllib.parse.urljoin(base, rel)
