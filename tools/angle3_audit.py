#!/usr/bin/env python3
"""Angle-3 live channel audit (Hindi-belt / betting-agent research).

Fetches t.me/s/<handle> previews and reports subscriber count, recent view
counts, last post date and post snippets, so a handle can be judged on real
reach and stated stake sizes rather than member count.

Usage:
  angle3_audit.py handle [handle ...]      # table
  angle3_audit.py --json handle [...]      # one JSON object per line
"""

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from html import unescape

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

TAG = re.compile(r"<[^>]+>")
VIEWS = re.compile(r'tgme_widget_message_views">([^<]+)<')
SUBS = re.compile(r'counter_value">([^<]+)</span>\s*<span class="counter_type">subscribers')
DATE = re.compile(r'<time datetime="([^"]+)"')
TEXT = re.compile(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', re.S)
OGT = re.compile(r'<meta property="og:title" content="([^"]*)"')
OGD = re.compile(r'<meta property="og:description" content="([^"]*)"')


def clean(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", " ", fragment)
    return re.sub(r"\s+", " ", unescape(TAG.sub("", fragment))).strip()


def num(txt: str) -> int:
    txt = txt.strip().upper().replace(" ", "").replace(",", "")
    mult = 1
    if txt.endswith("K"):
        mult, txt = 1_000, txt[:-1]
    elif txt.endswith("M"):
        mult, txt = 1_000_000, txt[:-1]
    try:
        return int(float(txt) * mult)
    except ValueError:
        return 0


def audit(handle: str) -> dict:
    handle = handle.strip().lstrip("@")
    res = {"handle": handle, "subs": 0, "views_med": 0, "views_max": 0,
           "last_post": "", "title": "", "desc": "", "posts": [], "state": "error"}
    try:
        html_doc = subprocess.run(
            ["curl", "-sL", "--max-time", "25", "-A", UA,
             f"https://t.me/s/{handle}"],
            capture_output=True, text=True, timeout=40).stdout
    except subprocess.TimeoutExpired:
        res["state"] = "timeout"
        return res
    if not html_doc:
        res["state"] = "empty"
        return res

    m = OGT.search(html_doc)
    res["title"] = unescape(m.group(1)) if m else ""
    m = OGD.search(html_doc)
    res["desc"] = re.sub(r"\s+", " ", unescape(m.group(1)))[:300] if m else ""
    m = SUBS.search(html_doc)
    res["subs"] = num(m.group(1)) if m else 0

    views = [num(v) for v in VIEWS.findall(html_doc)]
    if views:
        recent = views[-12:]
        res["views_med"] = sorted(recent)[len(recent) // 2]
        res["views_max"] = max(recent)
        res["views"] = recent

    dates = DATE.findall(html_doc)
    res["last_post"] = max(dates)[:10] if dates else ""
    res["posts"] = [p for p in (clean(t)[:260] for t in TEXT.findall(html_doc)) if p][-6:]

    body = " ".join(clean(t) for t in TEXT.findall(html_doc)).lower() + " " + res["desc"].lower()
    res["kw"] = {k: body.count(k) for k in
                 ("usdt", "trc20", "binance", "crypto", "upi", "inr", "lakh", "lac")
                 if body.count(k)}

    if views:
        res["state"] = "live"
    elif res["subs"] or res["title"]:
        res["state"] = "no_preview"
    else:
        res["state"] = "missing"
    return res


def main() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args
    handles = [a for a in args if not a.startswith("--")]
    if not handles:
        handles = [l.strip() for l in sys.stdin if l.strip()]

    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(audit, handles))

    if as_json:
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
        return

    rows.sort(key=lambda r: -r["views_med"])
    print(f"{'handle':34}{'state':11}{'subs':>8}{'med':>7}{'max':>7}  {'last':10} "
          f"{'keywords':28} title")
    for r in rows:
        kw = ",".join(f"{k}:{v}" for k, v in sorted(
            r.get("kw", {}).items(), key=lambda kv: -kv[1]))
        print(f"{r['handle'][:33]:34}{r['state']:11}{r['subs']:>8}"
              f"{r['views_med']:>7}{r['views_max']:>7}  "
              f"{(r['last_post'] or '-'):10} {kw[:28]:28} {r['title'][:34]}")


if __name__ == "__main__":
    main()
