#!/usr/bin/env python3
"""Harvest candidate Telegram handles from the lyzem public index.

Usage: tg_discover.py "query one" "query two" ...
Prints handle<TAB>hit_count<TAB>queries so frequently-matched channels surface first.
"""

import re
import subprocess
import sys
from collections import Counter, defaultdict
from urllib.parse import quote

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SKIP = {"lyzembot", "mlyzembot", "lyzemcom", "editorpost_bot", "s", "share",
        "joinchat", "addstickers", "proxy", "socks", "iv"}

LINK = re.compile(r"https://t\.me/(?:s/)?([A-Za-z0-9_]{4,32})")


def search(query: str, mode: str) -> list:
    url = f"https://lyzem.com/search?q={quote(query)}&type={mode}"
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, url],
                             capture_output=True, text=True, timeout=40).stdout
    except subprocess.TimeoutExpired:
        return []
    return [h for h in LINK.findall(out)
            if h.lower() not in SKIP and not h.lower().endswith("bot")]


def main() -> None:
    queries = sys.argv[1:]
    counts = Counter()
    where = defaultdict(set)
    for q in queries:
        for mode in ("messages", "channels"):
            for h in search(q, mode):
                counts[h] += 1
                where[h].add(q)
    for h, c in counts.most_common():
        print(f"{h}\t{c}\t{'; '.join(sorted(where[h]))[:120]}")


if __name__ == "__main__":
    main()
