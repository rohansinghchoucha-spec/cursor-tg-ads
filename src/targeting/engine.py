"""Channel / niche targeting brain for USDT trader acquisition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.models import CONFIG_DIR, load_json


@dataclass
class TargetingPack:
    niche_id: str
    label: str
    keywords: list[str]
    suggested_channels: list[str]
    geo: str | None
    payment_hooks: list[str]
    languages: list[str]
    score: float


class TargetingEngine:
    def __init__(self) -> None:
        self.data = load_json(CONFIG_DIR / "targeting.json")

    def niches(self) -> list[dict[str, Any]]:
        return sorted(self.data["niches"], key=lambda n: n.get("priority", 99))

    def geo_playbook(self, geo: str) -> dict[str, Any] | None:
        for g in self.data.get("geo_playbooks", []):
            if g["geo"].upper() == geo.upper():
                return g
        return None

    def build_pack(
        self,
        niche_id: str = "usdt_p2p",
        geo: str | None = None,
        extra_channels: list[str] | None = None,
    ) -> TargetingPack:
        niche = next((n for n in self.niches() if n["id"] == niche_id), self.niches()[0])
        play = self.geo_playbook(geo) if geo else None
        channels = list(niche.get("example_channels") or [])
        if extra_channels:
            channels.extend(extra_channels)
        # Dedupe preserve order
        seen: set[str] = set()
        uniq: list[str] = []
        for c in channels:
            if c.startswith("@") and c not in seen and c != "@":
                seen.add(c)
                uniq.append(c)
        priority = float(niche.get("priority", 3))
        score = max(0.1, 1.0 / priority)
        return TargetingPack(
            niche_id=niche["id"],
            label=niche["label"],
            keywords=list(niche.get("keywords") or []),
            suggested_channels=uniq[:100],
            geo=geo,
            payment_hooks=list((play or {}).get("payment_hooks") or []),
            languages=list((play or {}).get("languages") or ["en"]),
            score=score,
        )

    def rank_channels_for_offer(self, channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score channel dicts with keys: username, title, about, subs, niche_hint."""
        kw = set()
        for n in self.niches():
            for k in n.get("keywords") or []:
                kw.add(k.lower())

        ranked: list[dict[str, Any]] = []
        for ch in channels:
            blob = " ".join(
                [
                    str(ch.get("username", "")),
                    str(ch.get("title", "")),
                    str(ch.get("about", "")),
                    str(ch.get("niche_hint", "")),
                ]
            ).lower()
            hits = sum(1 for k in kw if k in blob)
            subs = int(ch.get("subs") or 0)
            # Prefer mid-size active trader channels
            size_score = 1.0
            if 5_000 <= subs <= 200_000:
                size_score = 1.5
            elif subs > 500_000:
                size_score = 0.8
            # Soft-penalize flash scam patterns
            penalty = 0.2 if "flash" in blob else 1.0
            score = hits * size_score * penalty
            ranked.append({**ch, "fit_score": round(score, 3)})
        ranked.sort(key=lambda x: x["fit_score"], reverse=True)
        return ranked
