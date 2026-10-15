#!/usr/bin/env python3
"""TGAdsSpy PUBLIC website client — never sends X-Api-Key.

Use this while Pro API is identity_quarantined (same cloud IP + API key).
Python/curl get Cloudflare 403. Real Chrome (port 9333) passes CF.

  python3 tools/spy_public.py ads "USDT" --geo IN
  python3 tools/spy_public.py advertiser tg-showxpay

Pace: 7s between navigations. Sequential. Stop on Just a moment / 429.
Do NOT call tools/spy_pro.py until memory/spy_reports.json api_lock lifts.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

import websocket

CDP = "http://127.0.0.1:9333"
GAP = 7.0
EXTRACT = r"""
(() => {
  const cards=[];
  document.querySelectorAll('a[href*="/ads/"]').forEach(a=>{
    const id=(a.href.match(/\/ads\/([a-z0-9]+)/)||[])[1];
    const t=(a.innerText||'').replace(/\s+/g,' ').trim();
    if(id && t.length>8) cards.push({id, href:a.href, text:t.slice(0,280)});
  });
  const handles=[...new Set((document.body.innerText||'').match(/@[A-Za-z0-9_]{4,32}/g)||[])];
  return {href:location.href, title:document.title,
          cards:cards.slice(0,40), handles:handles.slice(0,50),
          body:(document.body.innerText||'').slice(0,4000)};
})()
"""


def pages():
    return json.load(urllib.request.urlopen(f"{CDP}/json/list", timeout=5))


class Chrome:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, timeout=50)
        self.ws.settimeout(50)
        self.n = 17000
        self.call("Page.enable")
        self.call("Runtime.enable")

    def call(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(str(m["error"]))
                return m.get("result", {})

    def js(self, expr):
        return self.call("Runtime.evaluate", expression=expr, returnByValue=True).get("result", {}).get("value")

    def goto(self, url):
        self.call("Page.navigate", url=url)
        time.sleep(3.2)
        title = self.js("document.title") or ""
        if "Just a moment" in title:
            time.sleep(5)
            title = self.js("document.title") or ""
        if "Just a moment" in title:
            raise SystemExit("Cloudflare still up. Open tgadsspy.com in Chrome, pass CF, retry.")
        return title


def spy_page():
    for p in pages():
        if p.get("type") == "page" and "tgadsspy.com" in (p.get("url") or ""):
            return p
    # open a tab from any page
    any_p = next(p for p in pages() if p.get("type") == "page")
    c = Chrome(any_p["webSocketDebuggerUrl"])
    c.call("Target.createTarget", url="https://tgadsspy.com/ads")
    c.ws.close()
    time.sleep(2)
    return spy_page()


def fetch(url):
    p = spy_page()
    c = Chrome(p["webSocketDebuggerUrl"])
    c.goto(url)
    data = c.js(EXTRACT)
    c.ws.close()
    time.sleep(GAP)
    return data


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ads")
    a.add_argument("q")
    a.add_argument("--geo")
    b = sub.add_parser("advertiser")
    b.add_argument("slug")
    c = sub.add_parser("channels")
    c.add_argument("q")
    args = ap.parse_args()
    if args.cmd == "ads":
        url = "https://tgadsspy.com/ads?q=" + urllib.parse.quote(args.q)
        if args.geo:
            url += "&geo=" + urllib.parse.quote(args.geo)
    elif args.cmd == "advertiser":
        slug = args.slug if args.slug.startswith("tg-") else "tg-" + args.slug.lstrip("@").replace("_", "-")
        url = f"https://tgadsspy.com/advertisers/{slug}"
    else:
        url = "https://tgadsspy.com/channels?q=" + urllib.parse.quote(args.q)
    print(json.dumps(fetch(url), ensure_ascii=False, indent=2)[:16000])


if __name__ == "__main__":
    sys.exit(main())
