#!/usr/bin/env python3
"""Live-audit Telegram public channel previews (t.me/s/<handle>).

Prints subscriber count, recent post view counts, and sample post text so a
handle can be classified without opening Telegram.
"""
import concurrent.futures
import html
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def fetch(handle):
    url = f"https://t.me/s/{handle}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[ \t]+", " ", html.unescape(s)).strip()


def parse_count(txt):
    txt = txt.replace(" ", "").replace(",", "").replace("\u202f", "").lower()
    m = re.match(r"([\d.]+)([km]?)", txt)
    if not m:
        return 0
    n = float(m.group(1))
    return int(n * {"k": 1_000, "m": 1_000_000, "": 1}[m.group(2)])


def audit(handle):
    out = {"handle": handle}
    try:
        page = fetch(handle)
    except Exception as e:
        out["status"] = f"ERROR {e}"
        return out

    if "tgme_page_context_link" in page and "tgme_channel_info" not in page:
        out["status"] = "PRIVATE_OR_NO_PREVIEW"
        return out

    m = re.search(r'<span class="counter_value">([^<]+)</span>\s*<span class="counter_type">subscribers?</span>', page)
    out["subs"] = parse_count(m.group(1)) if m else None
    out["subs_raw"] = m.group(1) if m else None

    t = re.search(r'<div class="tgme_channel_info_header_title"[^>]*><span[^>]*>(.*?)</span>', page, re.S)
    out["title"] = strip_tags(t.group(1)) if t else None

    d = re.search(r'<div class="tgme_channel_info_description">(.*?)</div>', page, re.S)
    out["desc"] = strip_tags(d.group(1))[:400] if d else ""

    views = [parse_count(v) for v in re.findall(r'<span class="tgme_widget_message_views">([^<]+)</span>', page)]
    out["views"] = views[-12:]
    out["median_views"] = sorted(views)[len(views) // 2] if views else 0

    dates = re.findall(r'<time datetime="([^"]+)"', page)
    out["last_post"] = dates[-1] if dates else None

    bodies = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', page, re.S)
    out["posts"] = [strip_tags(b)[:600] for b in bodies[-4:]]

    if out["subs"] and out["median_views"]:
        out["view_ratio"] = round(out["median_views"] / out["subs"], 3)
    out["status"] = "OK"
    return out


def main():
    handles = [h.strip().lstrip("@") for h in sys.argv[1:] if h.strip()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(audit, handles):
            print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
