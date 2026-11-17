#!/usr/bin/env python3
"""Discover candidate Telegram handles by scraping @mentions / t.me links out of
public channel previews (t.me/s/<seed>).

Channels in the same niche cross-post and cross-promote, so mention graphs surface
inventory that keyword search never returns.

Usage:
    python3 tools/discover_mentions.py seed1 seed2 ... [--min-count 1] [--exclude file]
"""

import argparse
import collections
import concurrent.futures
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

MENTION = re.compile(r"(?:@|t\.me/)([A-Za-z][A-Za-z0-9_]{4,31})\b")

# Telegram infrastructure / generic noise that shows up on nearly every page.
NOISE = {
    "telegram", "share", "joinchat", "addstickers", "proxy", "socks", "durov",
    "telegramtips", "previews", "iv?url", "s/", "channel", "username",
}


def fetch(handle, timeout=25):
    req = urllib.request.Request(f"https://t.me/s/{handle}",
                                 headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def mentions_of(seed):
    try:
        html = fetch(seed)
    except Exception:  # noqa: BLE001 - a dead seed should not abort discovery
        return seed, []
    found = [m.lower() for m in MENTION.findall(html)]
    return seed, [m for m in found if m not in NOISE and m != seed.lower()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", nargs="+")
    ap.add_argument("--min-count", type=int, default=1)
    ap.add_argument("--exclude", help="file of handles to omit from output")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    excluded = set()
    if args.exclude:
        with open(args.exclude) as fh:
            excluded = {l.strip().lstrip("@").lower() for l in fh if l.strip()}

    counter = collections.Counter()
    sources = collections.defaultdict(set)
    seeds = [s.lstrip("@") for s in args.seeds]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for seed, found in pool.map(mentions_of, seeds):
            for handle in set(found):
                counter[handle] += 1
                sources[handle].add(seed)

    seed_set = {s.lower() for s in seeds}
    for handle, count in counter.most_common():
        if count < args.min_count or handle in excluded or handle in seed_set:
            continue
        print(f"{count:>3}  {handle:<36} from: {','.join(sorted(sources[handle])[:4])}")


if __name__ == "__main__":
    sys.exit(main())
