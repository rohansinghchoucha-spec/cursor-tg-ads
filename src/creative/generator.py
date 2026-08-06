"""AI + template creative generator for USDT trader ads."""

from __future__ import annotations

import json
import random
from typing import Any

from src.creative.compliance import is_safe_copy, sanitize_or_raise
from src.models import AdCreative, Settings, load_json, CONFIG_DIR

ANGLES = ("speed", "trust", "local_rails", "networks", "desk")

TEMPLATES: dict[str, list[dict[str, str]]] = {
    "en": [
        {
            "title": "USDT Desk — Fast P2P",
            "text": "Buy & sell USDT instantly. TRC20/BEP20/ERC20. Live rates. Verified desk — tap to start.",
            "cta": "Start Deal",
            "angle": "speed",
        },
        {
            "title": "Verified USDT OTC",
            "text": "Serious traders only. Secure USDT buy/sell, clear rates, professional support. Open chat.",
            "cta": "Talk to Desk",
            "angle": "trust",
        },
        {
            "title": "Local Pay → USDT",
            "text": "Convert local bank / UPI / transfer to USDT in minutes. All major networks. DM to lock rate.",
            "cta": "Get Live Rate",
            "angle": "local_rails",
        },
        {
            "title": "TRC20 USDT Ready",
            "text": "Low-fee TRC20 preferred. Also BEP20 & ERC20. Active desk for regular volume traders.",
            "cta": "Trade Now",
            "angle": "networks",
        },
    ],
    "hi": [
        {
            "title": "USDT Desk — UPI Fast",
            "text": "INR ↔ USDT instant. UPI/IMPS se deal. TRC20 available. Verified desk — abhi start karo.",
            "cta": "Deal Shuru Karo",
            "angle": "local_rails",
        },
        {
            "title": "Verified USDT P2P",
            "text": "Trusted USDT buy/sell. Live rate, clear process, support. Serious clients welcome.",
            "cta": "Rate Lo",
            "angle": "trust",
        },
    ],
    "es": [
        {
            "title": "USDT OTC Verificado",
            "text": "Compra y vende USDT rápido. TRC20/BEP20/ERC20. Tasas en vivo. Escritorio confiable.",
            "cta": "Empezar",
            "angle": "trust",
        }
    ],
    "ar": [
        {
            "title": "مكتب USDT موثوق",
            "text": "شراء وبيع USDT بسرعة. TRC20/BEP20/ERC20. أسعار مباشرة. تواصل الآن.",
            "cta": "ابدأ",
            "angle": "speed",
        }
    ],
    "ru": [
        {
            "title": "USDT OTC Desk",
            "text": "Покупка/продажа USDT. TRC20/BEP20/ERC20. Живой курс. Проверенный стол.",
            "cta": "Начать",
            "angle": "trust",
        }
    ],
}


SYSTEM_PROMPT = """You write Telegram Ads sponsored-message creatives for a legitimate USDT P2P/OTC desk.
Rules:
- Title max ~36 chars, body max ~150 chars
- No guaranteed profits, no 'x100', no risk-free, no flash USDT scams
- Emphasize speed, trust, networks (TRC20/BEP20/ERC20), local payment rails
- CTA must push user into a Telegram bot chat
- Return JSON array of objects: title, text, cta, language, angle, geo, niche_id
"""


class CreativeGenerator:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.campaign = load_json(CONFIG_DIR / "campaign.json")

    def templates(
        self,
        language: str = "en",
        n: int = 3,
        geo: str | None = None,
        niche_id: str = "usdt_p2p",
    ) -> list[AdCreative]:
        pool = TEMPLATES.get(language) or TEMPLATES["en"]
        picked = random.sample(pool, k=min(n, len(pool)))
        brand = self.campaign["product"].get("brand", "")
        out: list[AdCreative] = []
        for item in picked:
            title = item["title"]
            if brand and brand != "YOUR_BRAND" and len(title) < 28:
                title = f"{brand}: {title}"[:40]
            text = sanitize_or_raise(item["text"])
            out.append(
                AdCreative(
                    title=title[:40],
                    text=text[:160],
                    cta=item["cta"],
                    language=language,
                    geo=geo,
                    angle=item.get("angle", "trust"),
                    niche_id=niche_id,
                )
            )
        return out

    def generate_llm(
        self,
        language: str = "en",
        n: int = 5,
        geo: str | None = None,
        niche_id: str = "usdt_p2p",
        payment_hooks: list[str] | None = None,
    ) -> list[AdCreative]:
        if not self.settings.openai_api_key:
            return self.templates(language=language, n=n, geo=geo, niche_id=niche_id)

        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        product = self.campaign["product"]
        user = {
            "product": product,
            "language": language,
            "geo": geo,
            "niche_id": niche_id,
            "payment_hooks": payment_hooks or [],
            "count": n,
            "angles": list(ANGLES),
        }
        resp = client.chat.completions.create(
            model=self.campaign.get("llm", {}).get("model", "gpt-4o-mini"),
            temperature=float(self.campaign.get("llm", {}).get("temperature", 0.7)),
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(user)
                    + '\nReturn {"creatives":[...]}',
                },
            ],
        )
        raw = json.loads(resp.choices[0].message.content or "{}")
        items: list[dict[str, Any]] = raw.get("creatives") or raw.get("ads") or []
        creatives: list[AdCreative] = []
        for item in items:
            blob = f"{item.get('title','')} {item.get('text','')}"
            ok, _ = is_safe_copy(blob)
            if not ok:
                continue
            creatives.append(
                AdCreative(
                    title=str(item.get("title", ""))[:40],
                    text=str(item.get("text", ""))[:160],
                    cta=str(item.get("cta", "Start")),
                    language=str(item.get("language", language)),
                    geo=item.get("geo") or geo,
                    angle=str(item.get("angle", "trust")),
                    niche_id=str(item.get("niche_id", niche_id)),
                )
            )
        if not creatives:
            return self.templates(language=language, n=n, geo=geo, niche_id=niche_id)
        return creatives[:n]
