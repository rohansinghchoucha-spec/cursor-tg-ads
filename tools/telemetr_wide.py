#!/usr/bin/env python3
"""Wide (not seed-channel) Telemetr Advanced hunt for India USDT sellers.

Uses AdsSearch2 + Search2 pagination (no Export). Canonical verdicts still
need a human live t.me/s pass — this only gathers candidates.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict

sys.path.insert(0, "/workspace")
from tools.telemetr_gw import try_rpc, search, get_by_id
from tools.telemetr_hunt import resolve_id, COOKIE_PATH
from tools.audit_channels import audit

OUT = "/workspace/local/hunt/wide"
os.makedirs(OUT, exist_ok=True)

DR = {"from": "2026-06-03T00:00:00.000Z", "to": "2026-09-03T23:59:59.999Z"}
INDIA = {"dateRange": DR, "sourceCountries": [{"countryId": "india"}]}

INTENT_TERMS = [
    "we buy USDT",
    "sell USDT",
    "USDT to INR",
    "USDT UPI",
    "P2P USDT",
    "USDT seller",
    "cashout USDT",
    "USDT payout",
    "buy USDT UPI",
    "INR USDT rate",
]

EXTRA_LANES = [
    "freelancer USDT",
    "USDT remittance",
    "prop firm payout",
    "funded account payout",
    "USDT withdrawal India",
    "OTC USDT India",
    "Binance P2P India",
]

FORM_TERMS = [
    "usdt p2p",
    "usdt otc india",
    "we buy usdt",
    "usdt seller india",
    "inr usdt",
    "binance p2p",
    "usdt freelancer",
    "usdt payout",
    "dubai usdt",
    "crypto p2p india",
    "usdt cashout",
    "sell usdt upi",
]

JUNK_TITLE = re.compile(
    r"loot|matka|satta|rummy|aviator|1win|manhwa|movie|gift.?code|hack|"
    r"signal|leverage|futures|airdrop|mining|parity|color trad|"
    r"cosplay|birthday|prediction|wingo|tiranga",
    re.I,
)
BLOCK = {
    "cryptoamanclub", "officialcryptoindia", "cryptopointhi", "pushpendrasinghofficial",
    "startfromzerofamily", "bitcoinexpertindia", "cryptohindio", "cryptoshyamcs",
    "wazirx", "zebpayofficial", "coindcxofficial", "powerofstocks", "showxpay",
    "fundednextofficialcommunity", "bullishbull", "cryptokaroo",
}


def ads_pages(term, pages=6):
    cursor = None
    chats, msgs = {}, []
    for i in range(pages):
        payload = {"filter": INDIA, "term": term, "returnShortInfo": True}
        if cursor:
            payload["cursor"] = cursor
        st, body = try_rpc("store.v1.Messages/AdsSearch2", payload)
        if st != 200 or not isinstance(body, dict):
            print("ADS_FAIL", term, i, st, str(body)[:120])
            break
        for c in body.get("chats") or []:
            iid = (c.get("id") or {}).get("internalId")
            if iid:
                chats[iid] = c
        for m in body.get("messages") or []:
            msgs.append(m)
        cursor = body.get("cursor")
        print("ADS", term, "p", i, "count", body.get("count"), "chats", len(chats), "msgs", len(msgs))
        if not cursor:
            break
        time.sleep(0.25)
    return chats, msgs


def search2_bundle(term):
    st, body = try_rpc("store.v1.Messages/Search2", {"filter": INDIA, "term": term, "returnShortInfo": True})
    if st != 200:
        print("S2_FAIL", term, st, str(body)[:120])
        return {}, [], []
    chats = {}
    for c in body.get("chats") or []:
        iid = (c.get("id") or {}).get("internalId")
        if iid:
            chats[iid] = c
    sources = body.get("sources") or []
    cats = body.get("categories") or []
    print("S2", term, "count", body.get("count"), "sources", body.get("sourcesCount"), "chats", len(chats), "cats", [x.get("category", {}).get("slug") for x in cats[:4]])
    time.sleep(0.2)
    return chats, sources, cats


def keep_chat(c):
    user = (c.get("username") or "").lstrip("@")
    if not user or user.lower() in BLOCK:
        return False
    title = c.get("title") or ""
    if JUNK_TITLE.search(title) or JUNK_TITLE.search(user):
        return False
    flags = c.get("collectorFlags") or {}
    if flags.get("cheater") or flags.get("blocked"):
        return False
    country = ((c.get("country") or {}).get("id") or {}).get("countryId") or (
        (c.get("country") or {}).get("countryId")
    )
    # keep india OR unknown (many china-pay have country None)
    if country and country not in ("india", "in"):
        return False
    members = c.get("membersCount") or 0
    if members < 900 or members > 120000:
        return False
    cats = c.get("category") or []
    slugs = []
    if isinstance(cats, list):
        for x in cats:
            if isinstance(x, dict):
                slugs.append((x.get("slug") or x.get("categoryId") or "").lower())
            else:
                slugs.append(str(x).lower())
    slug_s = " ".join(slugs)
    if slug_s and any(k in slug_s for k in ("bets", "casino", "movies", "adult", "erotica", "games")):
        return False
    return True


def main():
    all_chats = {}
    sources_by_term = {}
    ads_msgs = []

    for term in INTENT_TERMS + EXTRA_LANES:
        ch, msgs = ads_pages(term, pages=4)
        ads_msgs.extend(msgs)
        all_chats.update(ch)
        ch2, sources, cats = search2_bundle(term)
        all_chats.update(ch2)
        sources_by_term[term] = sources

    form_hits = []
    for term in FORM_TERMS:
        st, body = search(term)
        n = len((body or {}).get("items") or [])
        print("FORM", term, st, (body or {}).get("count"), n)
        for it in (body or {}).get("items") or []:
            if it.get("peer") != "PEER_TYPE_CHANNEL":
                continue
            form_hits.append(it)
            iid = (it.get("id") or {}).get("internalId")
            if iid:
                all_chats.setdefault(iid, it)
        time.sleep(0.15)

    # hydrate sources (often no username)
    cache = {}
    if os.path.exists("/workspace/local/hunt/id_cache.json"):
        cache = json.load(open("/workspace/local/hunt/id_cache.json"))
    resolved_sources = []
    seen_src = set()
    for term, sources in sources_by_term.items():
        for s in sources:
            iid = (s.get("channel") or {}).get("internalId")
            if not iid or iid in seen_src:
                continue
            seen_src.add(iid)
            info = resolve_id(iid, cache)
            info["messagesCount"] = s.get("messagesCount")
            info["membersCount"] = s.get("membersCount")
            info["term"] = term
            resolved_sources.append(info)
            print(" SRC", term, info.get("handle"), info.get("membersCount"), s.get("messagesCount"))

    json.dump(cache, open("/workspace/local/hunt/id_cache.json", "w"))
    json.dump(
        {
            "chats": list(all_chats.values()),
            "form_hits": len(form_hits),
            "resolved_sources": resolved_sources,
        },
        open(f"{OUT}/raw.json", "w"),
        ensure_ascii=False,
        indent=2,
    )

    candidates = []
    for iid, c in all_chats.items():
        if keep_chat(c):
            candidates.append(c)
    # also source handles
    source_handles = []
    for r in resolved_sources:
        h = (r.get("handle") or "").strip()
        if h and h.lower() not in BLOCK and not JUNK_TITLE.search(h):
            source_handles.append(h)

    handles = []
    for c in candidates:
        handles.append(c.get("username"))
    handles.extend(source_handles)
    handles = [h for h in handles if h]
    # unique preserve order
    seen = set()
    uniq = []
    for h in handles:
        k = h.lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(h)
    print("CANDIDATE_HANDLES", len(uniq))
    json.dump(uniq, open(f"{OUT}/handles.json", "w"))
    json.dump(candidates, open(f"{OUT}/chats_filtered.json", "w"), ensure_ascii=False, indent=2)

    # audit first 80 new-looking
    audits = []
    for h in uniq[:80]:
        a = audit(h)
        audits.append(a)
        print("LIVE", h, a.get("subscribers"), a.get("views_median"), a.get("days_stale"), (a.get("title") or "")[:40])
        time.sleep(0.35)
    json.dump(audits, open(f"{OUT}/audits.json", "w"), ensure_ascii=False, indent=2)
    print("DONE audits", len(audits), "handles", len(uniq))


if __name__ == "__main__":
    main()
