#!/usr/bin/env python3
"""Full Telemetr Advanced hunt: search + ads placements + live audit.

Saves gitignored JSON under local/hunt/. Auto KEEP in verdict.json is DIRTY
(keyword collisions: futures signals, loot, Egypt TrustPay, Paytm). Canonical
verdicts live only in memory/CHANNEL_RESEARCH.md + memory/channels.json after
a human live t.me/s pass. Never copy auto-KEEP into an ad pack.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from html import unescape
from collections import Counter, defaultdict

sys.path.insert(0, "/workspace")
from tools.telemetr_gw import search, try_rpc
from tools.audit_channels import audit

COOKIE_PATH = "/workspace/local/telemetr_cookies.json"
OUTDIR = "/workspace/local/hunt"
os.makedirs(OUTDIR, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

SEARCH_TERMS = [
    "diwapay", "linkpay", "linkxwallet", "mobiuspe", "mobius pay", "lgpay",
    "999pay", "wallet_999pay", "trustpay", "atgpay", "hoyopay", "showpay",
    "mmoney", "ultrapay", "jaypay", "quickpay", "bhaartpay", "wiseway",
    "alexpay", "meteorpay", "ezpay", "zkpay", "upay wallet",
    "we buy usdt", "usdt sell india", "usdt to inr", "sell usdt upi",
    "usdt buyer", "p2p usdt india", "inr usdt rate",
]

# known DROP/HATA/education — skip even if Telemetr returns them
BLOCK = {
    "cryptoamanclub", "officialcryptoindia", "cryptopointhi", "pushpendrasinghofficial",
    "startfromzerofamily", "bitcoinexpertindia", "cryptohindio", "cryptoshyamcs",
    "wazirx", "wazirxofficial", "zebpayofficial", "coindcxofficial", "powerofstocks",
    "mobiuspetech", "linkpay_en", "hoyopay777", "showxpay",
}

LOOT_RE = re.compile(
    r"loot|gift.?code|matka|satta|rummy|aviator|1win|hack|flash usdt|forex signal|prop firm",
    re.I,
)
EARN_RE = re.compile(r"earn(ing)? with|signup bonus|invite=|refer(ral)? bonus|task (app|earn)", re.I)


def cookie_header():
    cookies = json.load(open(COOKIE_PATH))
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies if c.get("name") and c.get("value"))


def resolve_id(internal_id, cache):
    if internal_id in cache:
        return cache[internal_id]
    req = urllib.request.Request(
        f"https://telemetr.io/en/cc/{internal_id}",
        headers={"User-Agent": UA, "Cookie": cookie_header(), "Accept": "text/html"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            url = r.geturl()
            html = r.read().decode("utf-8", "replace")[:12000]
    except Exception as e:
        cache[internal_id] = {"id": internal_id, "error": str(e)}
        return cache[internal_id]
    slug = None
    m = re.search(r"/channels/\d+-([A-Za-z0-9_]+)", url)
    if m:
        slug = m.group(1)
    ogh = re.search(r"Telegram channel @([A-Za-z0-9_]+)", html)
    handle = (ogh.group(1) if ogh else None) or slug
    title = None
    og = re.search(r'property="og:title" content="([^"]+)"', html)
    if og:
        title = unescape(og.group(1)).split(" - ")[0]
    cache[internal_id] = {"id": internal_id, "handle": handle, "title": title, "url": url}
    time.sleep(0.35)
    return cache[internal_id]


def ads_for(internal_id):
    payload = {
        "filter": {
            "dateRange": {"from": "2026-06-03T00:00:00.000Z", "to": "2026-09-03T23:59:59.999Z"},
            "destChannel": {"internalId": internal_id, "telegramId": "0"},
        },
        "returnShortInfo": True,
    }
    st, body = try_rpc("store.v1.Messages/AdsSearch2", payload)
    return st, body


def main():
    cache = {}
    if os.path.exists(f"{OUTDIR}/id_cache.json"):
        cache = json.load(open(f"{OUTDIR}/id_cache.json"))

    searches = {}
    channel_hits = []
    for term in SEARCH_TERMS:
        st, body = search(term)
        searches[term] = {"status": st, "count": (body or {}).get("count"), "n": len((body or {}).get("items") or [])}
        print("SEARCH", term, searches[term])
        for it in (body or {}).get("items") or []:
            if it.get("peer") != "PEER_TYPE_CHANNEL":
                continue
            flags = (it.get("collectorFlags") or {})
            if flags.get("cheater") or flags.get("blocked"):
                continue
            iid = (it.get("id") or {}).get("internalId")
            if not iid:
                continue
            channel_hits.append({
                "term": term,
                "id": iid,
                "title": it.get("title"),
                "members": it.get("membersCount"),
                "cheater": flags.get("cheater"),
            })
        time.sleep(0.2)

    # unique by id
    by_id = {}
    for h in channel_hits:
        by_id.setdefault(h["id"], h)

    # seed ads from known good titles/ids
    seed_ids = []
    for iid, h in by_id.items():
        t = (h.get("title") or "").lower()
        if any(k in t for k in ("diwa", "linkpay", "linkx", "999pay", "lg pay", "lgpay", "mobius", "trustpay", "atg", "hoyo", "mmoney", "ultrapay", "jaypay", "quickpay", "alexpay", "wiseway", "showpay")):
            if h.get("members", 0) >= 1000:
                seed_ids.append(iid)
    seed_ids = list(dict.fromkeys(seed_ids))[:18]
    print("SEEDS", len(seed_ids))

    placement_ids = Counter()
    ads_meta = {}
    for sid in seed_ids:
        st, body = ads_for(sid)
        ads_meta[sid] = {"status": st, "count": (body or {}).get("count")}
        print("ADS", sid, ads_meta[sid])
        for msg in (body or {}).get("messages") or []:
            text = ((msg.get("message") or {}).get("message") or "")
            if LOOT_RE.search(text) or EARN_RE.search(text):
                continue
            for cid in msg.get("chatIds") or []:
                iid = cid.get("internalId")
                if iid:
                    placement_ids[iid] += 1
        time.sleep(0.25)

    # resolve top placement channels + search hits with members>=1500
    to_resolve = list(placement_ids.keys())
    for iid, h in by_id.items():
        if h.get("members", 0) >= 1500:
            to_resolve.append(iid)
    to_resolve = list(dict.fromkeys(to_resolve))[:80]
    print("RESOLVE", len(to_resolve))
    resolved = []
    for iid in to_resolve:
        info = resolve_id(iid, cache)
        info["placement_ads"] = placement_ids.get(iid, 0)
        if iid in by_id:
            info["members"] = by_id[iid].get("members")
            info["title"] = info.get("title") or by_id[iid].get("title")
        resolved.append(info)
        print(" ", info.get("handle"), info.get("members"), info.get("placement_ads"))

    json.dump(cache, open(f"{OUTDIR}/id_cache.json", "w"))
    json.dump({"searches": searches, "ads_meta": ads_meta, "resolved": resolved}, open(f"{OUTDIR}/raw.json", "w"), ensure_ascii=False, indent=2)

    handles = []
    for r in resolved:
        h = (r.get("handle") or "").strip()
        if not h or h.lower() in BLOCK:
            continue
        if LOOT_RE.search(r.get("title") or "") or LOOT_RE.search(h):
            continue
        handles.append(h)
    handles = list(dict.fromkeys(handles))[:60]
    print("AUDIT", handles)
    audits = []
    for h in handles:
        a = audit(h)
        audits.append(a)
        print("LIVE", h, a.get("subscribers"), a.get("views_median"), a.get("days_stale"), a.get("error") or a.get("public_preview"))
        time.sleep(0.4)

    json.dump(audits, open(f"{OUTDIR}/audits.json", "w"), ensure_ascii=False, indent=2)

    keep = []
    drop = []
    for a in audits:
        h = a.get("handle")
        if a.get("error") or a.get("public_preview") is False:
            drop.append({**a, "why": "restricted_or_error"})
            continue
        subs = a.get("subscribers") or 0
        med = a.get("views_median")
        age = a.get("days_stale")
        sample = " ".join([a.get("title") or "", a.get("description") or "", " ".join(a.get("samples") or [])])
        if LOOT_RE.search(sample) or EARN_RE.search(sample):
            drop.append({**a, "why": "loot_earn"})
            continue
        if med is None:
            drop.append({**a, "why": "no_views"})
            continue
        if age is not None and age > 21:
            drop.append({**a, "why": f"stale_{age}d"})
            continue
        if subs and med and subs > 5000 and med < 80:
            drop.append({**a, "why": "inflated"})
            continue
        if subs < 800:
            drop.append({**a, "why": "too_small_ads_reject"})
            continue
        keep.append(a)

    json.dump({"keep": keep, "drop": drop}, open(f"{OUTDIR}/verdict.json", "w"), ensure_ascii=False, indent=2)
    print("KEEP", len(keep), "DROP", len(drop))
    for a in keep:
        print(" +", a.get("handle"), a.get("subscribers"), a.get("views_median"), a.get("days_stale"))


if __name__ == "__main__":
    main()
