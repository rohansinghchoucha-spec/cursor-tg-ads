"""Premium stills for Nexa Desk / USDT P2P Venezuela channel."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "media"
ASSETS = Path("/opt/cursor/artifacts/assets")
LOCAL_ASSETS = ROOT / "assets" / "brand"
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

# Premium palette
INK = (6, 24, 38)
TEAL = (15, 90, 94)
AMBER = (212, 160, 50)
WHITE = (248, 250, 252)
MUTED = (186, 198, 206)

BRAND_MAP = {
    "trust_escrow": "brand_confianza.png",
    "pago_movil": "brand_pago_movil.png",
    "trust_wallet": "brand_hero_usdt_ve.png",
    "tasa_vs_binance": "brand_hero_usdt_ve.png",
    "scams": "brand_confianza.png",
    "trc20": "brand_hero_usdt_ve.png",
    "sell_order": "brand_orden_venta.png",
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT), size)


def ensure_brand_assets() -> None:
    LOCAL_ASSETS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if ASSETS.exists():
        for name in BRAND_MAP.values():
            src = ASSETS / name
            if src.exists():
                dst = LOCAL_ASSETS / name
                if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                    dst.write_bytes(src.read_bytes())


def _fallback_canvas(title: str, subtitle: str, path: Path) -> Path:
    w, h = 1080, 1350
    img = Image.new("RGB", (w, h), INK)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        r = int(INK[0] * (1 - t) + TEAL[0] * t * 0.55)
        g = int(INK[1] * (1 - t) + TEAL[1] * t * 0.55)
        b = int(INK[2] * (1 - t) + TEAL[2] * t * 0.55)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    draw.rectangle([64, 64, 200, 70], fill=AMBER)
    draw.text((64, 110), "NEXA DESK", font=_font(28, True), fill=AMBER)
    y = 420
    title_f = _font(58, True)
    for word_line in _wrap(draw, title, title_f, w - 128):
        draw.text((64, y), word_line, font=title_f, fill=WHITE)
        y += 72
    y += 24
    sub_f = _font(34)
    for word_line in _wrap(draw, subtitle, sub_f, w - 128):
        draw.text((64, y), word_line, font=sub_f, fill=MUTED)
        y += 46
    draw.text((64, h - 100), "USDT P2P · Venezuela", font=_font(26), fill=MUTED)
    img.save(path, quality=95)
    return path


def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
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
    filename: str | None = None,
    post_id: str | None = None,
) -> Path:
    ensure_brand_assets()
    OUT.mkdir(parents=True, exist_ok=True)
    name = filename or "post.png"
    path = OUT / name

    asset_name = BRAND_MAP.get(post_id or "", "")
    asset = LOCAL_ASSETS / asset_name if asset_name else None
    if asset and asset.exists():
        img = Image.open(asset).convert("RGB")
        img = img.resize((1080, 1350), Image.Resampling.LANCZOS)
        # subtle contrast polish
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = ImageEnhance.Color(img).enhance(1.05)
        # thin amber frame
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1079, 1349], outline=AMBER, width=3)
        img.save(path, quality=96)
        return path

    return _fallback_canvas(title, subtitle, path)


def make_short_video(image_path: Path, seconds: int = 5) -> Path:
    out = image_path.with_suffix(".mp4")
    # Slow zoom for more premium feel
    vf = (
        "scale=1200:1500,"
        "zoompan=z='min(1.08,1+0.0015*on)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1350:fps=25"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-vf",
        vf,
        "-t",
        str(seconds),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out
