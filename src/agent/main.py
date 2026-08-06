"""Main AI agent loop: plan → create → optimize for USDT TG ads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.creative.generator import CreativeGenerator
from src.integrations.backends import get_backend, ADSLYNotes, MCPBridgeNotes, TelegaNotes
from src.models import CampaignPlan, Settings, CONFIG_DIR, DATA_DIR, load_json
from src.optimizer.rules import CampaignOptimizer
from src.targeting.engine import TargetingEngine

console = Console()


class USDTAdsAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.campaign_cfg = load_json(CONFIG_DIR / "campaign.json")
        self.creatives = CreativeGenerator(self.settings)
        self.targeting = TargetingEngine()
        self.optimizer = CampaignOptimizer()
        self.backend = get_backend(self.settings)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def plan(
        self,
        niche_id: str = "usdt_p2p",
        geo: str | None = "IN",
        language: str | None = None,
        channel_usernames: list[str] | None = None,
        n_creatives: int = 4,
    ) -> CampaignPlan:
        pack = self.targeting.build_pack(niche_id=niche_id, geo=geo, extra_channels=channel_usernames)
        lang = language or (pack.languages[0] if pack.languages else "en")
        creatives = self.creatives.generate_llm(
            language=lang,
            n=n_creatives,
            geo=geo,
            niche_id=niche_id,
            payment_hooks=pack.payment_hooks,
        )
        cabinet = self.campaign_cfg.get("cabinet", {})
        plan = CampaignPlan(
            name=f"{niche_id}_{geo or 'global'}_{lang}_{datetime.now(tz=timezone.utc).strftime('%Y%m%d')}",
            niche_id=niche_id,
            channels=pack.suggested_channels,
            creatives=creatives,
            cpm=float(cabinet.get("min_cpm_ton", 0.1)),
            budget=float(cabinet.get("default_budget_ton", 5)),
            cabinet=str(cabinet.get("preferred", "TON")),
        )
        out = DATA_DIR / f"plan_{plan.name}.json"
        out.write_text(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))
        console.print(f"[green]Plan saved[/green] → {out}")
        return plan

    def launch(self, plan: CampaignPlan) -> dict:
        product = self.campaign_cfg["product"]
        if "YOUR_LEAD_BOT" in str(product.get("cta_url", "")):
            console.print("[yellow]Warning:[/yellow] Set real cta_url / bot in config/campaign.json")
        result = self.backend.create_campaign(plan)
        console.print(result)
        return result

    def optimize_once(self) -> list:
        metrics = self.backend.fetch_metrics()
        actions = self.optimizer.decide(metrics)
        if not actions:
            console.print("[cyan]No optimizer actions needed.[/cyan]")
            return []
        table = Table(title="Optimizer actions")
        table.add_column("Ad")
        table.add_column("Action")
        table.add_column("Reason")
        for a in actions:
            table.add_row(a.ad_id, a.action, a.reason)
        console.print(table)
        return self.backend.apply_actions(actions)

    def print_stack_guide(self) -> None:
        console.rule("World stack — pehle se ready")
        console.print(MCPBridgeNotes.SETUP)
        console.print(ADSLYNotes.SETUP)
        console.print(TelegaNotes.SETUP)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="USDT Telegram Ads AI Agent")
    parser.add_argument("command", choices=["plan", "launch", "optimize", "demo", "stack"])
    parser.add_argument("--niche", default="usdt_p2p")
    parser.add_argument("--geo", default="IN")
    parser.add_argument("--lang", default=None)
    parser.add_argument("--channels", default="", help="Comma-separated @channels")
    args = parser.parse_args()

    agent = USDTAdsAgent()
    channels = [c.strip() for c in args.channels.split(",") if c.strip()]

    if args.command == "stack":
        agent.print_stack_guide()
        return

    if args.command == "plan":
        plan = agent.plan(niche_id=args.niche, geo=args.geo, language=args.lang, channel_usernames=channels)
        console.print_json(data=plan.model_dump())
        return

    if args.command == "launch":
        plan = agent.plan(niche_id=args.niche, geo=args.geo, language=args.lang, channel_usernames=channels)
        agent.launch(plan)
        return

    if args.command == "optimize":
        agent.optimize_once()
        return

    if args.command == "demo":
        plan = agent.plan(niche_id=args.niche, geo=args.geo, language=args.lang or "hi", channel_usernames=channels or ["@example_usdt_desk"])
        launched = agent.launch(plan)
        ad_id = launched["ad_id"]
        # Simulate weak CTR → pause
        agent.backend.seed_demo_metrics(ad_id, impressions=6000, clicks=5)
        console.rule("After weak performance")
        agent.optimize_once()
        # Simulate winner
        agent.backend.seed_demo_metrics(ad_id, impressions=8000, clicks=120)
        # re-activate for demo scale path
        data_path = Path(DATA_DIR / "dry_run_campaigns.json")
        raw = json.loads(data_path.read_text())
        for m in raw["metrics"]:
            if m["ad_id"] == ad_id:
                m["status"] = "active"
        data_path.write_text(json.dumps(raw, indent=2))
        console.rule("After strong performance")
        agent.optimize_once()


if __name__ == "__main__":
    main()
