#!/usr/bin/env python3
"""Mine app brand names and links from promo-board channels.

Boards that advertise "top buy-sell apps" list many China-pay wallets per post.
This walks a few pages of t.me/s/<board> history and counts:
  - brand words ending in pay/wallet/pe (e.g. ShaktiPay, QQPay, HoYoPay)
  - t.me handles and invite-link hosts
  - registration / APK domains

Usage:
    python3 tools/board_mine.py board1 board2 ... [--pages 6]
"""
import argparse
import collections
import html
import re
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BRAND = re.compile(r"\b([A-Za-z][A-Za-z0-9]{1,14}(?:\s?(?:pay|PAY|Pay|wallet|Wallet|WALLET|pe|Pe|PE)))\b")
HANDLE = re.compile(r"(?:@|t\.me/)([A-Za-z][A-Za-z0-9_]{4,31})\b")
URL = re.compile(r"https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
SKIP_HOSTS = {"t.me", "telegram.org", "youtube.com", "youtu.be", "www.youtube.com", "chat.whatsapp.com", "forms.gle"}


def fetch(handle, before=None):
    url = f"https://t.me/s/{handle}" + (f"?before={before}" if before else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def text_of(page):
    bodies = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', page, re.S)
    out = []
    for b in bodies:
        hrefs = re.findall(r'href="([^"]+)"', b)
        s = re.sub(r"<br\s*/?>", "\n", b)
        s = re.sub(r"<[^>]+>", " ", s)
        out.append(html.unescape(s) + "\n" + "\n".join(html.unescape(h) for h in hrefs))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("boards", nargs="+")
    ap.add_argument("--pages", type=int, default=6)
    a = ap.parse_args()

    brands, handles, hosts = collections.Counter(), collections.Counter(), collections.Counter()
    for board in a.boards:
        before = None
        for _ in range(a.pages):
            try:
                page = fetch(board, before)
            except Exception as e:  # noqa: BLE001 - a dead page should not stop the rest
                print(f"# {board} fetch error {e}")
                break
            ids = [int(x) for x in re.findall(rf'data-post="{re.escape(board)}/(\d+)"', page, re.I)]
            for t in text_of(page):
                for b in BRAND.findall(t):
                    brands[re.sub(r"\s+", "", b).lower()] += 1
                for h in HANDLE.findall(t):
                    handles[h.lower()] += 1
                for host in URL.findall(t):
                    host = host.lower()
                    if host not in SKIP_HOSTS:
                        hosts[host] += 1
            if not ids or min(ids) <= 1:
                break
            before = min(ids)
            time.sleep(0.6)
        print(f"# mined {board}")

    print("\n## brands")
    for k, v in brands.most_common(80):
        print(f"{v:4d}  {k}")
    print("\n## handles")
    for k, v in handles.most_common(120):
        print(f"{v:4d}  {k}")
    print("\n## hosts")
    for k, v in hosts.most_common(80):
        print(f"{v:4d}  {k}")


if __name__ == "__main__":
    main()
