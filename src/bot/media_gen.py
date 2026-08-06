"""Generate simple branded stills + short mp4 clips for channel posts."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "media"
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

# Brand palette — Venezuela P2P desk, not purple AI-default
BG_TOP = (8, 47, 73)  # deep teal
BG_BOT = (15, 118, 110)  # teal
ACCENT = (251, 191, 36)  # amber
TEXT = (255, 255, 255)
MUTED = (204, 251, 241)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT
    return ImageFont.truetype(str(path), size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def make_post_image(
    title: str,
    subtitle: str,
    footer: str = "USDT P2P Venezuela · Trust Wallet",
    filename: str | None = None,
) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    w, h = 1080, 1350
    img = Image.new("RGB", (w, h), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # accent bar
    draw.rectangle([0, 0, w, 18], fill=ACCENT)
    draw.rectangle([60, 220, 180, 232], fill=ACCENT)

    brand = _font(36, bold=True)
    title_f = _font(64, bold=True)
    sub_f = _font(40)
    foot_f = _font(28)

    draw.text((60, 80), "USDT P2P · VE", font=brand, fill=ACCENT)

    y = 260
    for line in _wrap(draw, title, title_f, w - 120):
        draw.text((60, y), line, font=title_f, fill=TEXT)
        y += 78

    y += 30
    for line in _wrap(draw, subtitle, sub_f, w - 120):
        draw.text((60, y), line, font=sub_f, fill=MUTED)
        y += 52

    draw.text((60, h - 120), footer, font=foot_f, fill=MUTED)
    draw.text((60, h - 70), "@p2pupdatescheck", font=foot_f, fill=ACCENT)

    name = filename or "post.png"
    path = OUT / name
    img.save(path, quality=95)
    return path


def make_short_video(image_path: Path, seconds: int = 4) -> Path:
    """Ken-burns-ish static video from image via ffmpeg."""
    out = image_path.with_suffix(".mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-c:v",
        "libx264",
        "-t",
        str(seconds),
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "scale=1080:1350",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out
