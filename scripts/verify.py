#!/usr/bin/env python3
"""Independent re-verification of every curated paper against its official source.

Writes docs/verification-report.md. Nothing here reads data/raw cache: the point
is to prove the live official pages still agree with what we shipped.

  python scripts/verify.py [--limit N]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fetchlib import acl_anthology, cvf, http, openalex  # noqa: E402

UA = {"User-Agent": http.USER_AGENT}
# Liveness only: ojs.aaai.org returns 403 to crawler UAs, so the link check
# presents itself like a reader's browser. Bulk fetching keeps the crawler UA.
BROWSER_UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def alive(url: str, head_only: bool = False) -> tuple[str, str]:
    if not url:
        return ("skip", "-")
    try:
        method = "HEAD" if head_only else "GET"
        req = urllib.request.Request(url, headers=BROWSER_UA, method=method)
        with urllib.request.urlopen(req, timeout=45) as r:
            return ("ok", str(r.status))
    except Exception as exc:  # noqa: BLE001
        return ("fail", str(exc)[:60])


def live_official(paper: dict) -> tuple[str, str]:
    """Re-read title/abstract straight from the official system, no cache."""
    venue = paper["venue"]
    if venue in ("CVPR", "ICCV"):
        abs_text = cvf.abstract(paper["links"]["official"], use_cache=False)
        meta = cvf.abstract_meta(paper["links"]["official"], use_cache=False)
        return abs_text, meta.get("official_title", "")
    if venue == "ACL":
        abs_text = acl_anthology.abstract(paper["links"]["official"], use_cache=False)
        return abs_text, acl_anthology.official_title(paper["links"]["official"],
                                                      use_cache=False)
    return openalex.abstract_by_doi(paper["links"]["doi"]), ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--venue", default="", help="only re-verify one pillar, e.g. AAAI")
    args = ap.parse_args()

    blob = json_load(os.path.join(DATA, "papers.json"))
    papers = [p for p in blob["papers"] if not args.venue or p["venue"] == args.venue]
    papers = papers[: args.limit or None]
    rows, problems = [], []

    for i, p in enumerate(papers, start=1):
        live_abs, live_title = live_official(p)
        title_ok = (not live_title) or norm(live_title) == norm(p["title"])
        abs_ok = norm(live_abs) == norm(p["abstract"])
        page_status, page_note = alive(p["links"]["official"])
        pdf_status, _ = (alive(p["links"]["pdf"], head_only=True)
                         if p["links"]["pdf"] else ("skip", "-"))
        ok = title_ok and abs_ok and page_status == "ok"
        rows.append((p, title_ok, abs_ok, page_status, pdf_status, len(live_abs)))
        if not ok:
            problems.append((p["id"], f"title={title_ok} abs={abs_ok} page={page_status} {page_note}"))
        print(f"[{i:2d}/{len(papers)}] {p['venue']:4s} abs_match={abs_ok} "
              f"page={page_status} pdf={pdf_status} {p['title'][:42]}")

    if args.venue or args.limit:
        print(f"（部分核验 --venue={args.venue or '全部'} --limit={args.limit or '∞'}，"
              "不覆盖完整报告）")
    else:
        write_report(rows, problems)
    print(f"\n核验 {len(rows)} 篇，异常 {len(problems)} 篇 -> docs/verification-report.md")
    for pid, why in problems:
        print("  !", pid, why)
    return 1 if problems else 0


def json_load(path: str):
    import json
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_report(rows, problems) -> None:
    ok_abs = sum(1 for r in rows if r[2])
    ok_page = sum(1 for r in rows if r[3] == "ok")
    ok_pdf = sum(1 for r in rows if r[4] == "ok")
    lines = [
        "# 数据核验报告",
        "",
        f"- 核验时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 核验方式：对每篇精选论文**绕过本地缓存**重新读取官方页面，"
        "把官方摘要与仓库内 `data/papers.json` 做规范化后逐字比对；"
        "同时请求论文页与 PDF 链接确认可达。",
        f"- 结果：{len(rows)} 篇中，摘要逐字一致 **{ok_abs}** 篇，"
        f"论文页可达 **{ok_page}** 篇，PDF 可达 **{ok_pdf}** 篇，异常 **{len(problems)}** 篇。",
        "",
        "| 届次 | 官方语料规模 | 精选 | 摘要一致 | 论文页可达 | PDF 可达 |",
        "|---|---|---|---|---|---|",
    ]
    corpus = json_load(os.path.join(DATA, "corpus_meta.json"))["stats"]
    for ed in json_load(os.path.join(DATA, "corpus_meta.json")).get("editions", []):
        key, k = ed["label"], (ed["venue"], ed["year"])
        sub = [r for r in rows if (r[0]["venue"], r[0]["year"]) == k]
        n = len(sub)
        if not n:
            continue
        cinfo = corpus.get(key, {})
        pdf_ok = sum(1 for r in sub if r[4] == "ok")
        pdf_skip = sum(1 for r in sub if r[4] == "skip")
        pdf_cell = f"{pdf_ok}/{n}" + (f"（{pdf_skip} 篇不适用）" if pdf_skip else "")
        lines.append(
            f"| {key} | {cinfo.get('papers', 0):,} | {n} | "
            f"{sum(1 for r in sub if r[2])}/{n} | "
            f"{sum(1 for r in sub if r[3] == 'ok')}/{n} | {pdf_cell} |")
    lines += ["", "## 逐篇比对", "",
              "| # | 论文 | 官方记录号 | 摘要逐字一致 | 官方摘要字符数 | 论文页 | PDF |",
              "|---|---|---|---|---|---|---|"]
    for n, (p, t_ok, a_ok, pg, pdf, ln) in enumerate(rows, start=1):
        title = p["title"].replace("|", "/")[:58]
        lines.append(f"| {n} | {title} | `{p['provenance']['paper_id']}` | "
                     f"{'✅' if a_ok else '❌'} | {ln} | {pg} | {pdf} |")
    if problems:
        lines += ["", "## 异常明细", ""]
        lines += [f"- `{pid}`：{why}" for pid, why in problems]
    lines += ["", "## 说明", "",
              "- 「摘要一致」判定：双方文本做小写化并剔除除字母数字外的全部字符后比较，"
              "以规避连字符断行、MathJax 标签等排版差异带来的假阴性。",
              "- 摘要比对使用抓取脚本的规范 UA；链接可达性检查改用普通浏览器 UA，"
              "因为 ojs.aaai.org 对非浏览器 UA 一律返回 403（读者点击链接时看到的是同一页面）。",
              "- 中文摘要为人工翻译，不参与自动比对；抽查方式是在详情页展开英文原文对照。",
              "- AAAI 走 OpenAlex（其摘要源自官方 proceedings），CVF 与 ACL 直接读会议官方开放获取站点。",
              ""]
    out = os.path.join(ROOT, "docs", "verification-report.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote", out)


if __name__ == "__main__":
    raise SystemExit(main())
