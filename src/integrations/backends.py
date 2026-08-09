"""Adapters for ADSLY, telegram_ads_mcp, Telega.io, and dry-run local store."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.models import AdMetrics, CampaignPlan, OptimizeAction, DATA_DIR, Settings


class AdsBackend(ABC):
    @abstractmethod
    def create_campaign(self, plan: CampaignPlan) -> dict[str, Any]:
        ...

    @abstractmethod
    def apply_actions(self, actions: list[OptimizeAction]) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def fetch_metrics(self) -> list[AdMetrics]:
        ...


class DryRunBackend(AdsBackend):
    """Local JSON ledger — safe default until real cabinet credentials exist."""

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path = DATA_DIR / "dry_run_campaigns.json"
        if not self.path.exists():
            self._write({"campaigns": [], "metrics": [], "actions_log": []})

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text())

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2))

    def create_campaign(self, plan: CampaignPlan) -> dict[str, Any]:
        data = self._read()
        ad_id = f"dry_{len(data['campaigns']) + 1}_{int(datetime.now(tz=timezone.utc).timestamp())}"
        record = {
            "ad_id": ad_id,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "plan": plan.model_dump(),
            "status": "active",
        }
        data["campaigns"].append(record)
        data["metrics"].append(
            {
                "ad_id": ad_id,
                "impressions": 0,
                "clicks": 0,
                "spend": 0.0,
                "status": "active",
            }
        )
        self._write(data)
        return {"ok": True, "dry_run": True, "ad_id": ad_id, "record": record}

    def apply_actions(self, actions: list[OptimizeAction]) -> list[dict[str, Any]]:
        data = self._read()
        results = []
        metrics_by_id = {m["ad_id"]: m for m in data["metrics"]}
        for a in actions:
            entry = {"action": a.model_dump(), "applied_at": datetime.now(tz=timezone.utc).isoformat()}
            m = metrics_by_id.get(a.ad_id)
            if m and a.action == "pause":
                m["status"] = "paused"
            data["actions_log"].append(entry)
            results.append({"ok": True, "dry_run": True, **entry})
        self._write(data)
        return results

    def fetch_metrics(self) -> list[AdMetrics]:
        data = self._read()
        return [AdMetrics(**m) for m in data["metrics"]]

    def seed_demo_metrics(self, ad_id: str, impressions: int, clicks: int) -> None:
        data = self._read()
        for m in data["metrics"]:
            if m["ad_id"] == ad_id:
                m["impressions"] = impressions
                m["clicks"] = clicks
                m["spend"] = round(impressions / 1000 * 0.2, 4)
        self._write(data)


class MCPBridgeNotes:
    """How to wire Free-cat/telegram_ads_mcp (no browser session in this repo by default)."""

    SETUP = """
1. Clone https://github.com/Free-cat/telegram_ads_mcp
2. Login once to ads.telegram.org and save Playwright auth_state.json (NEVER commit)
3. Register MCP server in Cursor
4. Agent tools: list_ads, create_ad, set_cpm, set_status, increase_budget, get_ad_stats_csv
5. Always dry-run first (confirm=False), then confirm=True for spend
"""


class ADSLYNotes:
    SETUP = """
1. Create TON cabinet at ads.telegram.org and fund via Fragment
2. Sign up https://adsly.pro — connect cabinet
3. Enable IF/THEN rules mirroring config/campaign.json optimizer
4. Use this repo to generate creatives + channel packs, paste into ADSLY / API when available
"""


class TelegaNotes:
    SETUP = """
Telega.io = marketplace for native channel posts (not official sponsored ads).
Use for high-trust placements after spotting winning angles on TON Ads.
"""


def get_backend(settings: Settings | None = None) -> AdsBackend:
    settings = settings or Settings()
    # Real ADSLY/MCP adapters can replace DryRun when credentials exist.
    return DryRunBackend()
