#!/usr/bin/env python3
"""Pull Telegram Ads Spy creatives for a set of keywords and dump target channels.

With TGADSSPY_API_KEY (PRO) maxOffset is 50k; still pace requests — burst from
this cloud IP already triggered identity_quarantined 24h.
Anonymous cap remains offset 100.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://tgadsspy.com/api/v1/ads"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _key():
    return os.environ.get("TGADSSPY_API_KEY", "").strip()


def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if _key():
        headers["X-Api-Key"] = _key()
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(2.5)
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read()
            if e.code == 429 or b"identity_quarantined" in raw:
                print("STOP: Spy 429/quarantine — wait 24h", file=sys.stderr)
                return {"data": [], "error": "identity_quarantined"}
            time.sleep(2 + attempt)
        except Exception:
            time.sleep(2 + attempt)
    return {"data": []}


def pull(q):
    rows = []
    # PRO can page deeper; still stop early — we want CTAs not a dump.
    max_off = 400 if _key() else 100
    for off in range(0, max_off + 1, 20):
        d = get({"q": q, "limit": 20, "offset": off})
        if d.get("error") == "identity_quarantined":
            break
        batch = d.get("data", [])
        rows += batch
        if len(batch) < 20:
            break
    return q, rows


def main():
    queries = [a for a in sys.argv[1:]]
    seen = {}
    for q in queries:
        _, rows = pull(q)
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
