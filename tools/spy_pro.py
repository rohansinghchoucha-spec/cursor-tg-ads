#!/usr/bin/env python3
"""TGAdsSpy PRO client. Key from env only — never commit secrets.

    source /tmp/nexa_keys.env   # TGADSSPY_API_KEY
    python3 tools/spy_pro.py ads --q USDT --geo IN --limit 20
    python3 tools/spy_pro.py adload diwapay linkpay8
    python3 tools/spy_pro.py advertisers showx mobius

Pace is mandatory: this cloud IP already hit identity_quarantined (24h)
after a burst. Default 2.5s between calls. Abort on 429 quarantine.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://tgadsspy.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
MIN_GAP = 2.5
_last = 0.0


def load_key():
    key = os.environ.get("TGADSSPY_API_KEY", "").strip()
    if key:
        return key
    for env_path in ("/tmp/nexa_keys.env", "/workspace/local/nexa_keys.env"):
        if os.path.exists(env_path):
            for line in open(env_path):
                if line.startswith("export TGADSSPY_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("TGADSSPY_API_KEY missing. source /tmp/nexa_keys.env or local/nexa_keys.env first.")


def get(path, params=None, key=None):
    global _last
    wait = MIN_GAP - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    q = ("?" + urllib.parse.urlencode(params, doseq=True)) if params else ""
    url = BASE + path + q
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "X-Api-Key": key or load_key(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            _last = time.time()
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        _last = time.time()
        raw = e.read()
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_text": raw[:400].decode("utf-8", "replace")}
        if e.code == 429 or body.get("error") == "identity_quarantined":
            print("STOP: Spy identity_quarantined / 429. Wait 24h. Do not retry.", file=sys.stderr)
            print(json.dumps(body, ensure_ascii=False), file=sys.stderr)
            sys.exit(2)
        return e.code, body


def dump(st, data):
    print(json.dumps({"status": st, "body": data}, ensure_ascii=False, indent=2)[:8000])


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("ads")
    a.add_argument("--q")
    a.add_argument("--geo")
    a.add_argument("--advertiser")
    a.add_argument("--limit", type=int, default=20)
    a.add_argument("--offset", type=int, default=0)

    b = sub.add_parser("adload")
    b.add_argument("handles", nargs="+")

    c = sub.add_parser("advertisers")
    c.add_argument("query")
    c.add_argument("--limit", type=int, default=10)

    d = sub.add_parser("channel")
    d.add_argument("username")

    args = p.parse_args()
    key = load_key()
    if args.cmd == "ads":
        params = {"limit": args.limit, "offset": args.offset}
        if args.q:
            params["q"] = args.q
        if args.geo:
            params["geo"] = args.geo
        if args.advertiser:
            params["advertiser"] = args.advertiser
        dump(*get("/api/v1/ads", params, key))
    elif args.cmd == "adload":
        out = {}
        for h in args.handles:
            st, d = get("/api/v1/analytics/channel-ad-load", {"channelUsername": h.lstrip("@")}, key)
            out[h] = {"status": st, "body": d}
        print(json.dumps(out, ensure_ascii=False, indent=2)[:12000])
    elif args.cmd == "advertisers":
        dump(*get("/api/v1/advertisers", {"q": args.query, "limit": args.limit}, key))
    elif args.cmd == "channel":
        dump(*get(f"/api/v1/channels/{args.username.lstrip('@')}", key=key))


if __name__ == "__main__":
    main()
