"""USDT Telegram Ads AI Agent — shared models & settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"


def load_json(path: Path) -> dict[str, Any]:
    return orjson.loads(path.read_bytes())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""
    ads_cabinet: str = "TON"
    lead_webhook_url: str = ""
    dry_run: bool = True


class AdCreative(BaseModel):
    title: str = Field(max_length=40)
    text: str = Field(max_length=160)
    cta: str
    language: str = "en"
    geo: str | None = None
    angle: str = "trust"
    niche_id: str = "usdt_p2p"


class CampaignPlan(BaseModel):
    name: str
    niche_id: str
    channels: list[str]
    creatives: list[AdCreative]
    cpm: float
    budget: float
    cabinet: str = "TON"


class AdMetrics(BaseModel):
    ad_id: str
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    status: str = "active"

    @property
    def ctr(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return (self.clicks / self.impressions) * 100.0


class OptimizeAction(BaseModel):
    ad_id: str
    action: str
    reason: str
    params: dict[str, Any] = Field(default_factory=dict)
