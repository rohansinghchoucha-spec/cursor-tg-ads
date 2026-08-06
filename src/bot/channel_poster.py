"""Telegram channel poster via Bot API (admin bot)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"


def load_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("TELEGRAM_BOT_TOKEN missing — set in .env")


def api(token: str, method: str, **params):
    data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise SystemExit(f"HTTP {e.code}: {body}") from e


def discover_channels(token: str, timeout_sec: int = 120) -> list[dict]:
    """Long-poll getUpdates until channel admin/post events appear."""
    print("Waiting for channel events… Add @Rohanmcpbot as channel admin NOW.", flush=True)
    offset = None
    deadline = time.time() + timeout_sec
    found: dict[int, dict] = {}
    while time.time() < deadline:
        params: dict = {"timeout": 25, "limit": 100}
        if offset is not None:
            params["offset"] = offset
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/getUpdates", data=data
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.loads(r.read().decode())
        for u in payload.get("result") or []:
            offset = u["update_id"] + 1
            for key in ("my_chat_member", "channel_post", "message"):
                m = u.get(key)
                if not m:
                    continue
                chat = m.get("chat") or {}
                if chat.get("type") != "channel" and key != "my_chat_member":
                    continue
                if chat.get("type") == "channel" or (
                    key == "my_chat_member" and (chat.get("type") in {"channel", "supergroup"})
                ):
                    cid = chat.get("id")
                    found[cid] = {
                        "id": cid,
                        "title": chat.get("title"),
                        "username": chat.get("username"),
                        "type": chat.get("type"),
                        "event": key,
                    }
                    print("FOUND", found[cid], flush=True)
        if found:
            return list(found.values())
    return []


def post(token: str, chat_id: str, text: str) -> dict:
    return api(token, "sendMessage", chat_id=chat_id, text=text, disable_web_page_preview=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Channel bot helper")
    p.add_argument("command", choices=["me", "discover", "post", "check"])
    p.add_argument("--chat", default="", help="@channel or -100… id")
    p.add_argument("--text", default="MCP bot test ✅")
    p.add_argument("--wait", type=int, default=180)
    args = p.parse_args()
    token = load_token()

    if args.command == "me":
        print(json.dumps(api(token, "getMe"), indent=2))
        return

    if args.command == "discover":
        chans = discover_channels(token, timeout_sec=args.wait)
        out = ROOT / "data" / "channels.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(chans, indent=2, ensure_ascii=False))
        print("saved", out)
        if not chans:
            raise SystemExit("No channel events. Add bot as ADMIN with Post Messages, then retry.")
        return

    if args.command == "check":
        if not args.chat:
            raise SystemExit("--chat required")
        print(json.dumps(api(token, "getChat", chat_id=args.chat), indent=2, ensure_ascii=False))
        admins = api(token, "getChatAdministrators", chat_id=args.chat)
        print(json.dumps(admins, indent=2, ensure_ascii=False))
        return

    if args.command == "post":
        if not args.chat:
            # fallback to saved
            path = ROOT / "data" / "channels.json"
            if path.exists():
                chans = json.loads(path.read_text())
                if chans:
                    args.chat = str(chans[0]["id"])
            if not args.chat:
                raise SystemExit("--chat required (or run discover first)")
        res = post(token, args.chat, args.text)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if not res.get("ok"):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
