#!/usr/bin/env python3
"""Live-audit Telegram public channel previews (t.me/s/<handle>).

Prints: handle, title, subscriber count, recent post view counts (median/min/max),
last post age, and a text sample so seller intent can be judged by hand.

Usage:
    python3 tools/audit_channels.py handle1 handle2 ...
    python3 tools/audit_channels.py --file handles.txt [--json out.json]
"""

import argparse
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import unescape
from statistics import median

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

SUFFIX = {"K": 1_000, "M": 1_000_000}


def to_int(raw):
    raw = raw.strip().replace(",", "").replace("\u202f", "").replace("\xa0", "")
    m = re.match(r"^([\d.]+)\s*([KM])?$", raw, re.I)
    if not m:
        return None
    value = float(m.group(1))
    if m.group(2):
        value *= SUFFIX[m.group(2).upper()]
    return int(value)


def strip_tags(html):
    html = re.sub(r"<br\s*/?>", " ", html)
    html = re.sub(r"<[^>]+>", "", html)
    return unescape(re.sub(r"\s+", " ", html)).strip()


def fetch(handle, timeout=25):
    url = f"https://t.me/s/{handle}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def audit(handle):
    out = {"handle": handle}
    try:
        html = fetch(handle)
    except urllib.error.HTTPError as exc:
        out["error"] = f"HTTP {exc.code}"
        return out
    except Exception as exc:  # noqa: BLE001 - report any transport failure inline
        out["error"] = type(exc).__name__
        return out

    title = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    out["title"] = unescape(title.group(1)) if title else None

    desc = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    out["description"] = unescape(desc.group(1))[:300] if desc else None

    subs = re.search(r'<span class="counter_value">([^<]+)</span>\s*'
                     r'<span class="counter_type">subscribers</span>', html)
    out["subscribers"] = to_int(subs.group(1)) if subs else None

    if "tgme_widget_message " not in html and "tgme_widget_message\"" not in html:
        out["public_preview"] = False
    else:
        out["public_preview"] = True

    views = [to_int(v) for v in re.findall(r'<span class="tgme_widget_message_views">([^<]+)</span>', html)]
    views = [v for v in views if v is not None]
    out["view_samples"] = views[-12:]
    if views:
        recent = views[-12:]
        out["views_median"] = int(median(recent))
        out["views_min"] = min(recent)
        out["views_max"] = max(recent)
        if out["subscribers"]:
            out["view_ratio"] = round(out["views_median"] / out["subscribers"], 3)

    times = re.findall(r'<time datetime="([^"]+)"', html)
    if times:
        last = times[-1]
        try:
            dt = datetime.fromisoformat(last)
            out["last_post"] = dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            out["days_stale"] = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days
        except ValueError:
            out["last_post"] = last

    texts = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html, re.S)
    out["samples"] = [strip_tags(t)[:220] for t in texts[-5:] if strip_tags(t)]
    return out


def fmt(row):
    if row.get("error"):
        return f"{row['handle']:<34} ERROR {row['error']}"
    subs = row.get("subscribers")
    subs_s = f"{subs:,}" if subs else "?"
    if not row.get("public_preview"):
        return f"{row['handle']:<34} subs={subs_s:<10} PREVIEW-RESTRICTED  {row.get('title')}"
    med = row.get("views_median")
    ratio = row.get("view_ratio")
    return (f"{row['handle']:<34} subs={subs_s:<10} views med={med if med is not None else '?':<8}"
            f" [{row.get('views_min','?')}-{row.get('views_max','?')}]"
            f" ratio={ratio if ratio is not None else '?':<7} stale={row.get('days_stale','?')}d"
            f"  {row.get('title')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handles", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--json")
    ap.add_argument("--samples", action="store_true", help="print post text samples")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    handles = list(args.handles)
    if args.file:
        with open(args.file) as fh:
            handles += [l.strip().lstrip("@") for l in fh if l.strip() and not l.startswith("#")]
    handles = [h.lstrip("@") for h in handles]
    if not handles:
        ap.error("no handles given")

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(audit, handles):
            rows.append(row)

    order = {h.lower(): i for i, h in enumerate(handles)}
    rows.sort(key=lambda r: order.get(r["handle"].lower(), 0))
    for row in rows:
        print(fmt(row))
        if args.samples:
            for s in row.get("samples", []):
                print(f"      · {s}")
            print()

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rows, fh, indent=2)


if __name__ == "__main__":
    sys.exit(main())
