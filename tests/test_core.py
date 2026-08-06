from src.creative.compliance import is_safe_copy
from src.optimizer.rules import CampaignOptimizer
from src.models import AdMetrics
from src.targeting.engine import TargetingEngine


def test_compliance_blocks_guaranteed_returns():
    ok, hits = is_safe_copy("Guaranteed profit every day with USDT")
    assert not ok
    assert hits


def test_compliance_allows_honest_desk():
    ok, _ = is_safe_copy("Buy & sell USDT instantly. TRC20 available. Verified desk.")
    assert ok


def test_optimizer_pauses_low_ctr():
    opt = CampaignOptimizer(
        {
            "pause_if_ctr_below": 0.5,
            "pause_after_impressions": 1000,
            "scale_if_ctr_above": 2.0,
            "cpm_bump_percent": 10,
            "max_cpm_ton": 2.0,
        }
    )
    actions = opt.decide([AdMetrics(ad_id="a1", impressions=5000, clicks=5, status="active")])
    assert any(a.action == "pause" for a in actions)


def test_optimizer_scales_high_ctr():
    opt = CampaignOptimizer(
        {
            "pause_if_ctr_below": 0.2,
            "pause_after_impressions": 5000,
            "scale_if_ctr_above": 1.0,
            "cpm_bump_percent": 10,
            "max_cpm_ton": 2.0,
        }
    )
    actions = opt.decide(
        [AdMetrics(ad_id="a2", impressions=2000, clicks=40, status="active")],
        current_cpm={"a2": 0.2},
    )
    kinds = {a.action for a in actions}
    assert "raise_cpm" in kinds
    assert "duplicate_winner" in kinds


def test_targeting_pack_in():
    eng = TargetingEngine()
    pack = eng.build_pack("usdt_p2p", geo="IN", extra_channels=["@my_usdt", "@my_usdt"])
    assert pack.niche_id == "usdt_p2p"
    assert "UPI" in pack.payment_hooks
    assert pack.suggested_channels.count("@my_usdt") == 1


def test_rank_channels():
    eng = TargetingEngine()
    ranked = eng.rank_channels_for_offer(
        [
            {"username": "@flash_scam", "title": "FLASH USDT", "about": "flash", "subs": 50000},
            {"username": "@legit_p2p", "title": "USDT P2P OTC", "about": "buy sell TRC20", "subs": 40000},
        ]
    )
    assert ranked[0]["username"] == "@legit_p2p"
