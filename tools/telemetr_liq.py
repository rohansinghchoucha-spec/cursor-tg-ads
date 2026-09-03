#!/usr/bin/env python3
"""Liquidity / cash-out hunt for Indian USDT holders who want INR.

Fast path (no HTML scrape, no Export, no Spy):
  1) AdsSearch2 on BUYER creatives → placement chats already have username
  2) Search2 on tight HOLDER language only (skip noisy 10k+ terms)
  3) SearchForm OTC/desk catalog
  4) GetById for source IDs missing username (stableSlug)
  5) Live t.me/s only for handles NOT already in memory/
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import Counter

sys.path.insert(0, "/workspace")
from tools.telemetr_gw import try_rpc, search, get_by_id
from tools.audit_channels import audit

OUT = "/workspace/local/hunt/liq"
os.makedirs(OUT, exist_ok=True)

DR = {"from": "2026-06-03T00:00:00.000Z", "to": "2026-09-03T23:59:59.999Z"}
INDIA = {"dateRange": DR, "sourceCountries": [{"countryId": "india"}]}

BUYER_AD_TERMS = [
    "we buy USDT",
    "USDT to INR",
    "USDT UPI",
    "live rate USDT",
    "USDT IMPS",
    "buy USDT India",
    "USDT rate today",
    "we buy USDT UPI",
]

# Tight holder language only. Skip "USDT available" / "have USDT" (casino+signals dump).
HOLDER_TERMS = [
    "USDT sell karna",
    "USDT se paise",
    "INR chahiye USDT",
    "USDT holder",
    "bulk USDT",
    "OTC USDT",
    "USDT CDM",
    "USDT F2F",
    "USDT UPI me",
    "cashout USDT",
    "need INR",
    "USDT to bank",
]

FORM_TERMS = [
    "usdt buyer",
    "usdt otc",
    "usdt to inr",
    "usdt seller india",
    "usdt cdm",
    "otc desk india",
    "usdt p2p india",
]

JUNK_TITLE = re.compile(
    r"loot|matka|satta|rummy|aviator|1win|manhwa|movie|gift.?code|hack|"
    r"signal|leverage|futures|airdrop|mining|parity|color trad|"
    r"cosplay|birthday|prediction|wingo|tiranga|flash.?usdt|"
    r"forex signal|prop firm|fundednext|giveaway|giveway",
    re.I,
)
MULE_RE = re.compile(
    r"account (needed|required|wanted)|aadhaar|adhar|kyc id|"
    r"need bank|need upi id|qr (code )?needed|mule|"
    r"deposit usdt first|invite code|team commission|"
    r"part time (agent|work)|recruit",
    re.I,
)
LOOT_RE = re.compile(r"loot|gift.?code|rummy|aviator|1win|hack|flash usdt", re.I)
SELLER_HINT = re.compile(
    r"we buy|buy usdt|usdt to inr|upi|imps|neft|cdm|f2f|otc|"
    r"live rate|sell usdt|cash.?out|holder|liquidity|bech|nikal|"
    r"available.*usdt|have \d+",
    re.I,
)
CASINO_SLUG = ("bets", "casino", "movies", "adult", "erotica", "games")


def load_known():
    data = json.load(open("/workspace/memory/channels.json"))
    known = {}
    for k, v in (data.get("channels") or {}).items():
        if isinstance(v, dict):
            known[k.lower()] = v
    return known


def msg_text(m):
    inner = m.get("message") or {}
    if isinstance(inner, dict):
        return inner.get("message") or ""
    return str(inner or "")


def classify_ad(text):
    if LOOT_RE.search(text):
        return "loot"
    if MULE_RE.search(text):
        return "mule"
    if SELLER_HINT.search(text):
        return "buyer_ad_hunting_sellers"
    return "other"


def ads_pages(term, pages=6):
    cursor = None
    chats, msgs = {}, []
    for i in range(pages):
        payload = {"filter": INDIA, "term": term, "returnShortInfo": True}
        if cursor:
            payload["cursor"] = cursor
        st, body = try_rpc("store.v1.Messages/AdsSearch2", payload)
        if st != 200 or not isinstance(body, dict):
            print("ADS_FAIL", term, i, st, str(body)[:140], flush=True)
            break
        for c in body.get("chats") or []:
            iid = (c.get("id") or {}).get("internalId")
            if iid:
                chats[iid] = c
        for m in body.get("messages") or []:
            msgs.append(m)
        cursor = body.get("cursor")
        print("ADS", term, "p", i, "count", body.get("count"), "chats", len(chats), "msgs", len(msgs), flush=True)
        if not cursor:
            break
        time.sleep(0.18)
    return chats, msgs


def search2_bundle(term):
    st, body = try_rpc("store.v1.Messages/Search2", {"filter": INDIA, "term": term, "returnShortInfo": True})
    if st != 200:
        print("S2_FAIL", term, st, str(body)[:140], flush=True)
        return {}, []
    chats = {}
    for c in body.get("chats") or []:
        iid = (c.get("id") or {}).get("internalId")
        if iid:
            chats[iid] = c
    sources = body.get("sources") or []
    print(
        "S2", term, "count", body.get("count"), "sources", body.get("sourcesCount"),
        "chats", len(chats), flush=True,
    )
    time.sleep(0.12)
    return chats, sources


def keep_chat(c):
    user = (c.get("username") or "").lstrip("@")
    if not user:
        slug = c.get("stableSlug") or ""
        if "-" in slug:
            user = slug.split("-", 1)[-1]
    if not user:
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
    if country and country not in ("india", "in"):
        return False
    members = c.get("membersCount") or 0
    if members < 900 or members > 150000:
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
    if slug_s and any(k in slug_s for k in CASINO_SLUG):
        return False
    return True


def handle_of(c):
    user = (c.get("username") or "").lstrip("@")
    if user:
        return user
    slug = c.get("stableSlug") or ""
    if "-" in slug:
        return slug.split("-", 1)[-1]
    return None


def hydrate_id(iid, cache):
    if iid in cache:
        return cache[iid]
    st, body = get_by_id(internal_id=iid)
    info = {"id": iid, "status": st}
    if isinstance(body, dict):
        info["title"] = body.get("title")
        info["membersCount"] = body.get("membersCount")
        info["username"] = body.get("username")
        slug = body.get("stableSlug") or ""
        info["stableSlug"] = slug
        handle = body.get("username")
        if not handle and "-" in slug:
            handle = slug.split("-", 1)[-1]
        info["handle"] = handle
        info["about"] = (body.get("about") or "")[:240]
        country = body.get("country") or {}
        info["country"] = (country.get("id") or {}).get("countryId") or country.get("countryId")
        flags = body.get("collectorFlags") or {}
        info["cheater"] = flags.get("cheater")
        info["adsIndexGrade"] = body.get("adsIndexGrade")
    cache[iid] = info
    time.sleep(0.08)
    return info


def main():
    known = load_known()
    all_chats = {}
    ads_by_term = {}
    ad_class = Counter()
    placement_from_ads = Counter()
    ad_snippets = []

    for term in BUYER_AD_TERMS:
        ch, msgs = ads_pages(term, pages=6)
        ads_by_term[term] = {"chats": len(ch), "msgs": len(msgs)}
        all_chats.update(ch)
        for m in msgs:
            text = msg_text(m)
            cls = classify_ad(text)
            ad_class[cls] += 1
            if cls in ("loot", "mule"):
                continue
            for cid in m.get("chatIds") or []:
                iid = cid.get("internalId")
                if iid:
                    placement_from_ads[iid] += 1
            inner = m.get("message") or {}
            chid = (inner.get("channel") or {}).get("internalId") if isinstance(inner, dict) else None
            if chid:
                placement_from_ads[chid] += 1
            if len(ad_snippets) < 40 and cls == "buyer_ad_hunting_sellers":
                ad_snippets.append({"term": term, "text": text[:220], "views": m.get("maxViews")})

    sources_by_term = {}
    for term in HOLDER_TERMS:
        ch2, sources = search2_bundle(term)
        all_chats.update(ch2)
        sources_by_term[term] = sources[:8]

    form_hits = []
    for term in FORM_TERMS:
        st, body = search(term)
        n = len((body or {}).get("items") or [])
        print("FORM", term, st, (body or {}).get("count"), n, flush=True)
        for it in (body or {}).get("items") or []:
            if it.get("peer") != "PEER_TYPE_CHANNEL":
                continue
            form_hits.append(it)
            iid = (it.get("id") or {}).get("internalId")
            if iid:
                all_chats.setdefault(iid, it)
        time.sleep(0.1)

    # snapshot before hydrate
    json.dump(
        {
            "ads_by_term": ads_by_term,
            "ad_class": dict(ad_class),
            "ad_snippets": ad_snippets,
            "placement_ids": placement_from_ads.most_common(80),
            "chat_handles": [handle_of(c) for c in all_chats.values() if handle_of(c)],
        },
        open(f"{OUT}/ads_snapshot.json", "w"),
        ensure_ascii=False,
        indent=2,
    )
    print("SNAPSHOT chats", len(all_chats), "ad_class", dict(ad_class), flush=True)

    cache = {}
    if os.path.exists("/workspace/local/hunt/liq_id_cache.json"):
        cache = json.load(open("/workspace/local/hunt/liq_id_cache.json"))

    resolved = []
    seen = set()
    for term, sources in sources_by_term.items():
        for s in sources:
            iid = (s.get("channel") or {}).get("internalId")
            if not iid or iid in seen:
                continue
            seen.add(iid)
            info = hydrate_id(iid, cache)
            info["messagesCount"] = s.get("messagesCount")
            info["term"] = term
            resolved.append(info)
            print(" SRC", term, info.get("handle"), info.get("membersCount"), s.get("messagesCount"), (info.get("title") or "")[:40], flush=True)

    # hydrate top placements missing username
    for iid, n in placement_from_ads.most_common(30):
        if iid in all_chats and handle_of(all_chats[iid]):
            continue
        if iid in seen:
            continue
        seen.add(iid)
        info = hydrate_id(iid, cache)
        info["placement_hits"] = n
        info["term"] = "placement"
        resolved.append(info)
        print(" PLC", info.get("handle"), n, info.get("membersCount"), (info.get("title") or "")[:40], flush=True)

    json.dump(cache, open("/workspace/local/hunt/liq_id_cache.json", "w"))

    handles = []
    for c in all_chats.values():
        if keep_chat(c):
            handles.append(handle_of(c))
    for r in resolved:
        h = (r.get("handle") or "").strip()
        if not h or JUNK_TITLE.search(h) or r.get("cheater"):
            continue
        if r.get("country") and r["country"] not in ("india", "in"):
            continue
        members = r.get("membersCount") or 0
        if members and (members < 900 or members > 150000):
            continue
        handles.append(h)

    uniq = []
    seen_h = set()
    for h in handles:
        if not h:
            continue
        k = h.lstrip("@").lower()
        if k in seen_h:
            continue
        seen_h.add(k)
        uniq.append(h.lstrip("@"))

    new_handles = []
    known_skip = []
    for h in uniq:
        rec = known.get(h.lower())
        if rec:
            known_skip.append({"handle": h, "status": rec.get("status")})
            continue
        new_handles.append(h)

    print("UNIQ", len(uniq), "NEW", len(new_handles), "KNOWN", len(known_skip), flush=True)
    json.dump(
        {
            "ads_by_term": ads_by_term,
            "ad_class": dict(ad_class),
            "ad_snippets": ad_snippets,
            "uniq": uniq,
            "new_handles": new_handles,
            "known_skip": known_skip,
            "resolved": resolved,
            "form_hits": len(form_hits),
        },
        open(f"{OUT}/raw.json", "w"),
        ensure_ascii=False,
        indent=2,
    )
    json.dump(new_handles, open(f"{OUT}/new_handles.json", "w"))

    audits = []
    for h in new_handles[:80]:
        a = audit(h)
        audits.append(a)
        print(
            "LIVE", h, a.get("subscribers"), a.get("views_median"), a.get("days_stale"),
            (a.get("title") or a.get("error") or "")[:48],
            flush=True,
        )
        time.sleep(0.22)
    json.dump(audits, open(f"{OUT}/audits.json", "w"), ensure_ascii=False, indent=2)
    print("DONE new_audits", len(audits), "new", len(new_handles), flush=True)


if __name__ == "__main__":
    main()
