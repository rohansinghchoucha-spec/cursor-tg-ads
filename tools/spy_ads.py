#!/usr/bin/env python3
"""Pull Telegram Ads Spy creatives for a set of keywords and dump target channels.

The anonymous API caps offset at 100, so breadth comes from many narrow queries
rather than deep paging.
"""
import concurrent.futures
import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://tgadsspy.com/api/v1/ads"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(1 + attempt)
    return {"data": []}


def pull(q):
    rows = []
    for off in (0, 20, 40, 60, 80, 100):
        d = get({"q": q, "limit": 20, "offset": off})
        batch = d.get("data", [])
        rows += batch
        if len(batch) < 20:
            break
    return q, rows


def main():
    queries = [a for a in sys.argv[1:]]
    seen = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for q, rows in ex.map(pull, queries):
            print(f"# {q}: {len(rows)}", file=sys.stderr)
            for r in rows:
                u = r.get("ctaTargetUsername")
                if not u:
                    continue
                rec = seen.setdefault(
                    u.lower(),
                    {"handle": u, "geo": r.get("geo"), "lang": r.get("lang"), "n": 0, "queries": set(), "texts": set()},
                )
                rec["n"] += 1
                rec["queries"].add(q)
                t = (r.get("text") or "").replace("\n", " ")[:240]
                if t:
                    rec["texts"].add(t)
    out = []
    for rec in seen.values():
        rec["queries"] = sorted(rec["queries"])
        rec["texts"] = sorted(rec["texts"])[:3]
        out.append(rec)
    out.sort(key=lambda r: -r["n"])
    for rec in out:
        print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
