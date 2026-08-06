#!/usr/bin/env python3
"""Open ads.telegram.org for login; auto-save session when /account is reached."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Ensure package imports work when run as a file
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "telegram_ads_mcp" / "src"))

from telegram_ads_mcp.paths import ensure_secure_file, resolve_auth_state_path  # noqa: E402

BASE_URL = "https://ads.telegram.org/"
TIMEOUT_SEC = int(os.environ.get("AUTH_WAIT_SEC", "600"))


def main() -> None:
    auth_path = resolve_auth_state_path()
    print(f"Auth will save to: {auth_path}", flush=True)
    print("Browser opening — Telegram se login karo, account choose karo.", flush=True)
    print("Jab ads table (/account) dikhe, session auto-save ho jayega.", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
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
            # Success: logged in and past account chooser
            if "/account" in url and "choose_account" not in url:
                time.sleep(2)  # let table settle
                context.storage_state(path=str(auth_path))
                ensure_secure_file(auth_path)
                print(f"SUCCESS — session saved: {auth_path}", flush=True)
                browser.close()
                return
            time.sleep(1.5)

        context.storage_state(path=str(auth_path))
        ensure_secure_file(auth_path)
        print(
            f"TIMEOUT — partial state saved to {auth_path}. "
            "Agar choose_account pe atke ho to re-run after picking account.",
            flush=True,
        )
        browser.close()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
