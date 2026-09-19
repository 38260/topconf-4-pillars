#!/usr/bin/env python3
"""QA gate for the hand-translated Chinese fields.

Catches the two failure modes that actually happen when translating at scale:
English word leakage into Chinese fields, and topic ids that don't exist.
Lowercase English runs are the leak signal; proper nouns / acronyms / terms that
have no standard Chinese rendering (token, logits, KV cache) are allowed.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# lowercase terms deliberately kept in English inside Chinese text
ALLOW = {
    "token", "tokens", "logits", "patch", "patches", "bpp", "per", "vs", "via",
    "prompt", "prompts", "embedding", "embeddings", "pipeline", "pipelines",
    "fine", "tuning", "zero", "one", "shot", "pre", "post", "softmax", "layernorm",
    "query", "key", "value", "node", "nodes", "graph", "codebook", "codebooks",
    "checkpoint", "checkpoints", "benchmark", "baseline", "baselines", "dataset",
    "hop", "hops", "wiki", "web", "chat", "app", "apps", "e-commerce", "x",
    "tokenizer", "tokenizers", "miou", "iou", "dev", "psnr",
    "prefill", "decode", "post-hoc", "zero-shot", "bit", "val", "test", "alpha",
    "beta", "gamma", "top-k", "top-1", "top-5", "n-gram", "out-of-box", "iphone",
}

WORD = re.compile(r"[A-Za-z][A-Za-z\-']*")
CJK = re.compile(r"[\u4e00-\u9fff]")
URL = re.compile(r"https?://\S+")


def check(text: str) -> list[str]:
    """Flag lowercase English runs -- the shape an untranslated word takes."""
    text = URL.sub("", text)
    # （original term） after a Chinese term is intentional, not a leak
    text = re.sub(r"（[^（）]*）", " ", text)
    # metric prefixes glued to a number (top-1, W4A8, 2x) have no Chinese form
    text = re.sub(r"\b[a-z]{1,6}(?=--?\d)", "", text)
    bad = []
    for w in WORD.findall(text):
        w = w.rstrip("-'")
        if not w or w[0].isupper():       # proper nouns, method names, acronyms
            continue
        if w.lower() in ALLOW or len(w) < 3:
            continue
        bad.append(w.lower())
    return bad


def main() -> int:
    valid_topics = set(re.findall(r'"id": "([a-z0-9-]+)"',
                                  open(os.path.join(ROOT, "scripts", "topics.py"),
                                       encoding="utf-8").read()))
    tdir = os.path.join(DATA, "translations")
    errors = 0
    seen_ids = set()
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".json"):
            continue
        blob = json.load(open(os.path.join(tdir, fn), encoding="utf-8"))
        for t in blob["papers"]:
            seen_ids.add(t["id"])
            leaks = check(t["title_zh"]) + check(t["abstract_zh"])
            if leaks:
                print(f"  ! {fn} {t['id']} 英文残留: {sorted(set(leaks))}")
                errors += 1
            if not CJK.search(t["abstract_zh"]):
                print(f"  ! {fn} {t['id']} 译文无中文")
                errors += 1
            if len(t["abstract_zh"]) < 60:
                print(f"  ! {fn} {t['id']} 译文过短 ({len(t['abstract_zh'])} 字)")
                errors += 1
            for topic in t["topics"]:
                if topic not in valid_topics:
                    print(f"  ! {fn} {t['id']} 未知主题 {topic}")
                    errors += 1
            if not t.get("keywords"):
                print(f"  ! {fn} {t['id']} 无关键词")
                errors += 1
            for kw in t.get("keywords", []):
                if not kw.get("en") or not kw.get("zh"):
                    print(f"  ! {fn} {t['id']} 关键词缺中英项")
                    errors += 1
    print(f"译文条目 {len(seen_ids)} 篇，问题 {errors} 处")

    # second gate: the English source text must itself be complete
    dpath = os.path.join(DATA, "draft.json")
    if os.path.exists(dpath):
        draft = json.load(open(dpath, encoding="utf-8"))
        # a bare project/code URL is a legitimate way for an abstract to end
        complete = re.compile(r"([.!?\u201d\u2019)\]]|https?://\S+)\s*$")
        trunc = [p["id"] for p in draft
                 if not complete.search(p["abstract"].strip())]
        short = [p["id"] for p in draft if len(p["abstract"]) < 250]
        if trunc:
            print(f"  ! 英文摘要疑似被截断（{len(trunc)}）: {', '.join(trunc)}")
            errors += len(trunc)
        if short:
            print(f"  ! 英文摘要异常偏短（{len(short)}）: {', '.join(short)}")
            errors += len(short)
        print(f"英文原文体检：{len(draft)} 篇，截断 {len(trunc)}，偏短 {len(short)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
