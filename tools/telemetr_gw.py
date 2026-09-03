#!/usr/bin/env python3
"""Telemetr Advanced gateway client using saved Chrome cookies. Never commit cookies."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

COOKIE_PATH = "/workspace/local/telemetr_cookies.json"
GW = "https://gw-prod.telemetr.io"
GQL = "https://graphql.telemetr.io/graphql"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def cookie_header():
    cookies = json.load(open(COOKIE_PATH))
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies if c.get("name") and c.get("value"))


def headers():
    return {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://telemetr.io",
        "Referer": "https://telemetr.io/",
        "Cookie": cookie_header(),
    }


def post(url, payload, timeout=40):
    data = json.dumps(payload).encode() if payload is not None else b""
    req = urllib.request.Request(url, data=data, headers=headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            try:
                return r.status, json.loads(raw)
            except Exception:
                return r.status, {"_text": raw[:1500].decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw)
        except Exception:
            body = {"_text": raw[:800].decode("utf-8", "replace")}
        return e.code, body


def search(term, **extra):
    body = {"term": term}
    body.update(extra)
    return post(f"{GW}/store.v1.Chats/SearchForm", body)


def try_rpc(path, payload=None):
    return post(f"{GW}/{path}", payload if payload is not None else {})


def get_by_id(*, telegram_id=None, internal_id=None):
    chat_id = {}
    if telegram_id:
        chat_id["telegramId"] = str(telegram_id)
    if internal_id:
        chat_id["internalId"] = internal_id
    return try_rpc("store.v1.Chats/GetById", {"chatId": chat_id})


def mentions_in(telegram_id, limit=25, days=90):
    return try_rpc(
        "store.v1.Mentions/GetTopIncomingMentions",
        {
            "chatId": {"telegramId": str(telegram_id)},
            "limit": limit,
            "kind": 0,
            "period": {"daysAgo": days},
        },
    )


def similar_channels(telegram_id):
    """Telegram similar list. Empty until Export (credits). Do not Export."""
    return try_rpc(
        "store.v1.Chats/TgRecommendations",
        {"chatId": {"telegramId": str(telegram_id)}},
    )


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "search"
    if cmd == "search":
        term = sys.argv[2] if len(sys.argv) > 2 else "diwapay"
        st, data = search(term)
        print(json.dumps({"status": st, "body": data}, ensure_ascii=False)[:12000])
    elif cmd == "rpc":
        path = sys.argv[2]
        payload = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        st, data = try_rpc(path, payload)
        print(json.dumps({"status": st, "body": data}, ensure_ascii=False)[:8000])
    elif cmd == "get":
        handle_or_id = sys.argv[2]
        if handle_or_id.isdigit():
            st, data = get_by_id(telegram_id=handle_or_id)
        else:
            st, sbody = search(handle_or_id)
            items = (sbody or {}).get("items") or []
            iid = ((items[0] or {}).get("id") or {}).get("internalId") if items else None
            st, data = get_by_id(internal_id=iid) if iid else (st, sbody)
        print(json.dumps({"status": st, "body": data}, ensure_ascii=False)[:8000])
    elif cmd == "mentions":
        tgid = sys.argv[2]
        st, data = mentions_in(tgid)
        print(json.dumps({"status": st, "body": data}, ensure_ascii=False)[:8000])
    else:
        sys.exit("usage: telemetr_gw.py search TERM | get HANDLE|TGID | mentions TGID | rpc PATH [JSON]")
