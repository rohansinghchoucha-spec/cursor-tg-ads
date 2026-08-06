#!/usr/bin/env python3
"""Open ads.telegram.org; auto-save when dashboard is visible."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "telegram_ads_mcp" / "src"))

from playwright.sync_api import sync_playwright

from telegram_ads_mcp.paths import ensure_secure_file, resolve_auth_state_path

BASE_URL = "https://ads.telegram.org/"
TIMEOUT_SEC = int(os.environ.get("AUTH_WAIT_SEC", "900"))


def looks_logged_in(page) -> bool:
    url = page.url or ""
    if "choose_account" in url:
        return False
    if "/account" in url and "/auth" not in url:
        return True
    try:
        body = page.locator("body").inner_text(timeout=2000)
    except Exception:
        return False
    markers = ("Create a new ad", "Manage budget", "Views", "Actions")
    return sum(1 for m in markers if m in body) >= 2


def main() -> None:
    auth_path = resolve_auth_state_path()
    print(f"Auth will save to: {auth_path}", flush=True)
    print("Login browser ready. Phone/OTP ke baad dashboard aate hi auto-save.", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized", "--no-sandbox"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        deadline = time.time() + TIMEOUT_SEC
        last = ""
        while time.time() < deadline:
            url = page.url
            if url != last:
                print(f"URL: {url}", flush=True)
                last = url
            if looks_logged_in(page):
                time.sleep(2)
                context.storage_state(path=str(auth_path))
                ensure_secure_file(auth_path)
                print(f"SUCCESS — session saved: {auth_path}", flush=True)
                print(f"Final URL: {page.url}", flush=True)
                browser.close()
                return
            time.sleep(1.5)

        print("TIMEOUT — login complete nahi hua.", flush=True)
        browser.close()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
