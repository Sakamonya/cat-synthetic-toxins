#!/usr/bin/env python3
"""校验 sources 中的 quote 是否真的出现在对应页面正文里（需要联网）。

用法:
    python scripts/check_quotes.py            # 校验全部
    python scripts/check_quotes.py metaldehyde

环境变量:
    RESEARCH_PROXY   default http://127.0.0.1:7890
    NO_PROXY=1       直连

退出码: 0 = 全部通过（或没有可校验的 quote），1 = 有失败
"""

from __future__ import annotations

import html
import os
import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "synthetic-compounds.yaml"

PROXY = os.environ.get("RESEARCH_PROXY", "http://127.0.0.1:7890")
DIRECT = os.environ.get("NO_PROXY", "") == "1"
UA = "cat-toxins-quote-check/1.0"

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def make_opener():
    if DIRECT:
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    )


def fetch_text(op, url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with op.open(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", "replace")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    text = TAG_RE.sub(" ", raw)
    text = html.unescape(text)
    return WS_RE.sub(" ", text)


def norm(s: str) -> str:
    """归一化：引号、破折号、空白，以及剥标签产生的多余空格与引用角标。"""
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\[\s*\d+\s*\]", "", s)      # 去掉 [ 41 ] 这类引用角标
    s = WS_RE.sub(" ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)       # 标点前的空格
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    return s.strip()


def main() -> int:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    op = make_opener()

    checked = failed = skipped = 0
    cache: dict[str, str] = {}

    for e in entries:
        eid = e.get("id")
        if only and eid != only:
            continue
        for src in e.get("sources", []):
            quote = (src.get("quote") or "").strip()
            if not quote:
                continue
            url = src.get("url", "")
            checked += 1
            if url not in cache:
                try:
                    cache[url] = norm(fetch_text(op, url))
                except Exception as exc:  # noqa: BLE001
                    cache[url] = ""
                    print(f"[WARN] {eid}: 抓取失败 {url} ({str(exc)[:60]})")
            body = cache[url]
            if not body:
                skipped += 1
                print(f"[SKIP] {eid}: 无法抓取来源，跳过")
                continue
            if norm(quote) in body:
                print(f"[OK]   {eid}: {quote[:60]}…")
            else:
                failed += 1
                print(f"[FAIL] {eid}: 引文在页面中找不到")
                print(f"       quote: {quote[:120]}")
                print(f"       url  : {url}")

    print(f"\n检查 {checked} 条，通过 {checked - failed - skipped}，失败 {failed}，跳过 {skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
