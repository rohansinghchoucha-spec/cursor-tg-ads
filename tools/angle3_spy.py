#!/usr/bin/env python3
"""Mine tgadsspy for USDT-desk ad campaigns and the channels they place in.

Two modes:
  ads   <query>...   list ad campaign ids + creative text matching a query
  place <ad_id>...   list the channels a campaign was observed placing in
"""

import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

AD_ID = re.compile(r"/ads/([a-z0-9]{20,})")
PLACEMENT = re.compile(
    r'@(?:<!-- -->)?([A-Za-z0-9_]{4,32})(?:<!-- -->)?\s*·\s*'
    r'(?:<!-- -->)?([\d,]+)(?:<!-- -->)?\s*(?:<!-- -->)?\s*members')


def get(url: str) -> str:
    try:
        return subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, url],
                              capture_output=True, text=True, timeout=45).stdout
    except subprocess.TimeoutExpired:
        return ""


def unescape_payload(doc: str) -> str:
    return doc.replace('\\\\"', "'").replace('\\"', '"').replace("\\n", " ")


def ads(query: str) -> set:
    doc = get(f"https://tgadsspy.com/ads?q={quote(query)}")
    return set(AD_ID.findall(doc))


def placements(ad_id: str) -> list:
    doc = unescape_payload(get(f"https://tgadsspy.com/ads/{ad_id}"))
    return [(h, int(n.replace(",", ""))) for h, n in PLACEMENT.findall(doc)]


def main() -> None:
    mode, *args = sys.argv[1:]
    if mode == "ads":
        found = set()
        with ThreadPoolExecutor(max_workers=5) as pool:
            for s in pool.map(ads, args):
                found |= s
        for ad_id in sorted(found):
            print(ad_id)
    elif mode == "place":
        tally = Counter()
        size = {}
        with ThreadPoolExecutor(max_workers=5) as pool:
            for rows in pool.map(placements, args):
                for handle, members in rows:
                    tally[handle] += 1
                    size[handle] = max(size.get(handle, 0), members)
        for handle, hits in tally.most_common():
            print(f"{handle}\t{size[handle]}\t{hits}")


if __name__ == "__main__":
    main()
