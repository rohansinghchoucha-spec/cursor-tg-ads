#!/usr/bin/env python3
"""Harvest channel handles + names from the tgadsspy channel directory.

tgadsspy server-renders search hits into a JSON-LD ItemList, so a plain HTTP
fetch is enough. Usage: spy_search.py "query" ["query" ...]
"""

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

ITEM = re.compile(r'"url":"https://tgadsspy\.com/channels/([A-Za-z0-9_]{4,32})","name":"((?:[^"\\]|\\.)*)"')

GLOBAL_NOISE = {"telegram", "durov", "bitcoin", "hamster", "dogs", "notcoin",
                "star", "arcs", "duck", "dota", "tapswapai", "seedupdates",
                "blumcrypto", "majors", "roxman", "iroproxy", "imtproto",
                "proxymtproto", "km_ap", "catapult_extreme", "telegramtips",
                "cats_housewtf", "dogs_community", "hamster_kombat"}


def fetch(args) -> list:
    query, page = args
    url = f"https://tgadsspy.com/channels?q={quote(query)}"
    if page > 1:
        url += f"&page={page}"
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, url],
                             capture_output=True, text=True, timeout=45).stdout
    except subprocess.TimeoutExpired:
        return []
    out = out.replace('\\\\"', '\x00').replace('\\"', '"')
    hits = []
    for handle, name in ITEM.findall(out):
        if handle.lower() in GLOBAL_NOISE:
            continue
        name = name.replace('\x00', '"')
        try:
            name = json.loads(f'"{name}"')
        except json.JSONDecodeError:
            pass
        hits.append((handle, name, query))
    return hits


def main() -> None:
    queries = sys.argv[1:]
    jobs = [(q, p) for q in queries for p in (1, 2)]
    seen = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for batch in pool.map(fetch, jobs):
            for handle, name, query in batch:
                if handle not in seen:
                    seen[handle] = (name, query)
    for handle, (name, query) in seen.items():
        print(f"{handle}\t{name[:90]}\t[{query}]")


if __name__ == "__main__":
    main()
