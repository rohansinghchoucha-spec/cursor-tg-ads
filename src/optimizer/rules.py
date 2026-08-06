"""IF/THEN campaign optimizer for Telegram Ads metrics."""

from __future__ import annotations

from src.models import AdMetrics, OptimizeAction, CONFIG_DIR, load_json


class CampaignOptimizer:
    def __init__(self, rules: dict | None = None) -> None:
        campaign = load_json(CONFIG_DIR / "campaign.json")
        self.rules = rules or campaign.get("optimizer", {})

    def decide(self, metrics: list[AdMetrics], current_cpm: dict[str, float] | None = None) -> list[OptimizeAction]:
        current_cpm = current_cpm or {}
        actions: list[OptimizeAction] = []
        pause_ctr = float(self.rules.get("pause_if_ctr_below", 0.25))
        min_impr = int(self.rules.get("pause_after_impressions", 5000))
        scale_ctr = float(self.rules.get("scale_if_ctr_above", 1.2))
        bump = float(self.rules.get("cpm_bump_percent", 10))
        max_cpm = float(self.rules.get("max_cpm_ton", 2.0))

        for m in metrics:
            if m.status.lower() in {"on hold", "paused", "declined"}:
                if m.status.lower() == "declined" and self.rules.get("rewrite_on_moderation_fail"):
                    actions.append(
                        OptimizeAction(
                            ad_id=m.ad_id,
                            action="rewrite_creative",
                            reason="Moderation declined — rewrite & resubmit",
                        )
                    )
                continue

            if m.impressions >= min_impr and m.ctr < pause_ctr:
                actions.append(
                    OptimizeAction(
                        ad_id=m.ad_id,
                        action="pause",
                        reason=f"CTR {m.ctr:.2f}% < {pause_ctr}% after {m.impressions} impr",
                    )
                )
                continue

            if m.ctr >= scale_ctr and m.impressions >= max(1000, min_impr // 5):
                cpm = current_cpm.get(m.ad_id, 0.1)
                new_cpm = min(max_cpm, round(cpm * (1 + bump / 100.0), 4))
                if new_cpm > cpm:
                    actions.append(
                        OptimizeAction(
                            ad_id=m.ad_id,
                            action="raise_cpm",
                            reason=f"CTR {m.ctr:.2f}% strong — bump CPM {bump}%",
                            params={"cpm": new_cpm},
                        )
                    )
                actions.append(
                    OptimizeAction(
                        ad_id=m.ad_id,
                        action="duplicate_winner",
                        reason="Winning creative — duplicate to more channel packs",
                    )
                )
        return actions
