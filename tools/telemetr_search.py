#!/usr/bin/env python3
"""Bulk-search telemetr's open channel index and dump candidates as JSONL.

Anonymous plan allows 20 results per page up to offset 100, so coverage comes
from running many keywords rather than deep paging. Requests are paced because
the endpoint quarantines bursty clients.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://telemetr.com/api/v1/channels"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            if "data" in d:
                return d["data"]
            if d.get("error") == "identity_quarantined":
                time.sleep(5 * (attempt + 1))
                continue
            return []
        except Exception:
            time.sleep(2 * (attempt + 1))
    return []


def main():
    out = {}
    for q in sys.argv[1:]:
        got = 0
        for off in (0, 20, 40, 60, 80, 100):
            rows = get({"q": q, "limit": 20, "offset": off})
            if not rows:
                break
            got += len(rows)
            for c in rows:
                u = c.get("username")
                if not u:
                    continue
                rec = out.setdefault(u.lower(), dict(c, queries=[]))
                rec["queries"].append(q)
            time.sleep(0.35)
        print(f"# {q}: {got}", file=sys.stderr)
    for rec in out.values():
        print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
