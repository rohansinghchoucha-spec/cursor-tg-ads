#!/usr/bin/env python3
"""Telemetr.io Public API (api.tlmtr.io). Key from env only.

This is the BOT key product — NOT website Advanced $55.
Free key: search by @username works; catalog / info / mentions / add are locked.

    source /tmp/nexa_keys.env   # TELEMETR_API_KEY
    python3 tools/telemetr_api.py usage
    python3 tools/telemetr_api.py search @diwapay
    python3 tools/telemetr_api.py search-term USDT --country india --peer Channel
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.tlmtr.io"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def load_key():
    key = os.environ.get("TELEMETR_API_KEY", "").strip()
    if key:
        return key
    env_path = "/tmp/nexa_keys.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("export TELEMETR_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("TELEMETR_API_KEY missing. source /tmp/nexa_keys.env first.")


def get(path, params=None):
    q = ("?" + urllib.parse.urlencode(params, doseq=True)) if params else ""
    req = urllib.request.Request(
        BASE + path + q,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "x-api-key": load_key(),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_text": raw[:400].decode("utf-8", "replace")}
        return e.code, body


def dump(st, data):
    print(json.dumps({"status": st, "body": data}, ensure_ascii=False, indent=2)[:8000])


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("usage")
    s = sub.add_parser("search")
    s.add_argument("term", help="@handle or phrase")
    s.add_argument("--peer", default="Channel", choices=["Channel", "Group"])
    s.add_argument("--country")
    s.add_argument("--limit", type=int, default=20)
    t = sub.add_parser("search-term")
    t.add_argument("term")
    t.add_argument("--peer", default="Channel")
    t.add_argument("--country")
    t.add_argument("--about", action="store_true")
    t.add_argument("--limit", type=int, default=20)
    args = p.parse_args()
    if args.cmd == "usage":
        dump(*get("/v1/usage/info"))
        return
    params = {"term": args.term, "peer_type": args.peer, "limit": args.limit}
    if getattr(args, "country", None):
        params["country"] = args.country
    if getattr(args, "about", False):
        params["search_in_about"] = "true"
    dump(*get("/v1/channels/search", params))


if __name__ == "__main__":
    main()
