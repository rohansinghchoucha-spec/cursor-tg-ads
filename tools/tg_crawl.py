#!/usr/bin/env python3
"""Snowball-discover Telegram channels by harvesting t.me links out of previews.

Seeds are handles; every public preview page is scanned for outbound @handles
and t.me/<handle> links, which become the next frontier.
"""
import concurrent.futures
import json
import re
import sys
import urllib.request
from collections import Counter

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

NOISE = re.compile(
    r"^(s|c|joinchat|share|addstickers|proxy|socks|iv|telegram|telegramtips|durov|"
    r"BotFather|premiumbot|wallet|toncoin|blog|contest|previews)$",
    re.I,
)


def fetch(handle):
    req = urllib.request.Request(
        f"https://t.me/s/{handle}", headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def links_from(handle):
    try:
        page = fetch(handle)
    except Exception:
        return handle, []
    found = set()
    for h in re.findall(r"(?:https?://)?t\.me/([A-Za-z][A-Za-z0-9_]{3,31})", page):
        if not NOISE.match(h):
            found.add(h)
    for h in re.findall(r"@([A-Za-z][A-Za-z0-9_]{4,31})", page):
        if not NOISE.match(h):
            found.add(h)
    return handle, sorted(found)


def main():
    seeds = [h.strip().lstrip("@") for h in sys.argv[1:] if h.strip()]
    tally = Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        for src, hs in ex.map(links_from, seeds):
            for h in hs:
                tally[h] += 1
            print(f"# {src}: {len(hs)}", file=sys.stderr)
    seedset = {s.lower() for s in seeds}
    for h, n in tally.most_common():
        if h.lower() not in seedset:
            print(json.dumps({"handle": h, "seen": n}))


if __name__ == "__main__":
    main()
