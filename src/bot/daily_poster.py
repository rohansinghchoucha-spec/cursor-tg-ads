"""Daily auto-poster for @p2pupdatescheck — image + caption (+ short video)."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from src.bot.media_gen import make_post_image, make_short_video

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "daily_posts.json"
STATE = ROOT / "data" / "posts" / "state.json"
LOG = ROOT / "data" / "posts" / "history.jsonl"


def _token() -> str:
    t = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if t:
        return t
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("TELEGRAM_BOT_TOKEN missing")


def _chat() -> str:
    cfg = json.loads(CONFIG.read_text())
    return os.environ.get("TELEGRAM_CHANNEL") or cfg.get("channel") or "@p2pupdatescheck"


def _api(token: str, method: str, fields: dict | None = None, files: dict | None = None):
    """Simple multipart or form POST to Bot API."""
    url = f"https://api.telegram.org/bot{token}/{method}"
    if files:
        import uuid

        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
        body = b""
        for k, v in (fields or {}).items():
            body += f"--{boundary}\r\n".encode()
            body += f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode()
            body += f"{v}\r\n".encode()
        for name, (filename, raw, mime) in files.items():
            body += f"--{boundary}\r\n".encode()
            body += (
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            ).encode()
            body += f"Content-Type: {mime}\r\n\r\n".encode()
            body += raw + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
    else:
        data = urllib.parse.urlencode(fields or {}).encode()
        req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def pick_rotation(cfg: dict) -> dict:
    items = cfg["rotation"]
    # day-of-year rotation (Caracas-ish: use UTC-4 approx via env TZ if set)
    day = datetime.now().timetuple().tm_yday
    return items[day % len(items)]


def run(force_id: str | None = None, with_video: bool = True) -> dict:
    cfg = json.loads(CONFIG.read_text())
    STATE.parent.mkdir(parents=True, exist_ok=True)
    item = None
    if force_id:
        item = next((x for x in cfg["rotation"] if x["id"] == force_id), None)
    if item is None:
        item = pick_rotation(cfg)

    img = make_post_image(
        title=item["image_title"],
        subtitle=item["image_subtitle"],
        filename=f"{item['id']}.png",
    )
    video_path = None
    if with_video:
        try:
            video_path = make_short_video(img, seconds=4)
        except Exception as exc:  # noqa: BLE001
            print("video skip:", exc)

    token = _token()
    chat = _chat()
    caption = item["text"][:1024]

    # Prefer photo with caption (best reach); also send short video as follow-up if available
    photo_raw = img.read_bytes()
    res_photo = _api(
        token,
        "sendPhoto",
        fields={"chat_id": chat, "caption": caption},
        files={"photo": (img.name, photo_raw, "image/png")},
    )
    out = {"item": item["id"], "photo": res_photo, "at": datetime.now(timezone.utc).isoformat()}

    if video_path and video_path.exists() and res_photo.get("ok"):
        vraw = video_path.read_bytes()
        res_vid = _api(
            token,
            "sendVideo",
            fields={
                "chat_id": chat,
                "caption": f"🎬 {item['image_title']} — @p2pupdatescheck",
                "supports_streaming": "true",
            },
            files={"video": (video_path.name, vraw, "video/mp4")},
        )
        out["video"] = res_vid

    STATE.write_text(json.dumps({"last": out}, indent=2, ensure_ascii=False))
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": res_photo.get("ok"), "id": item["id"], "chat": chat}, ensure_ascii=False))
    if not res_photo.get("ok"):
        raise SystemExit(res_photo)
    return out


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--id", default=None, help="Force rotation id")
    p.add_argument("--no-video", action="store_true")
    args = p.parse_args()
    run(force_id=args.id, with_video=not args.no_video)


if __name__ == "__main__":
    main()
