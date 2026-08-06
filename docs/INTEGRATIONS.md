# MCP + ADSLY wiring

## A) telegram_ads_mcp (AI agent drives ads.telegram.org)

```bash
git clone https://github.com/Free-cat/telegram_ads_mcp.git
cd telegram_ads_mcp
# follow their README: Playwright login → auth_state.json
```

Cursor MCP config sketch:

```json
{
  "mcpServers": {
    "telegram-ads": {
      "command": "uv",
      "args": ["run", "python", "-m", "telegram_ads_mcp"],
      "env": {
        "AUTH_STATE_PATH": "/absolute/path/auth_state.json"
      }
    }
  }
}
```

Agent workflow with this repo:

1. `python -m src.agent.main plan --geo IN --lang hi`
2. Open `data/plan_*.json`
3. MCP tools: `create_ad` (confirm=False first), then `confirm=True`
4. Hourly: `get_ad_stats_csv` → feed metrics into `CampaignOptimizer` → `set_cpm` / `set_status`

## B) ADSLY

1. Connect TON / Stars / Euro cabinet
2. Mirror optimizer from `config/campaign.json`:
   - IF CTR < 0.25% AND impressions > 5000 → pause
   - IF CTR > 1.2% → raise CPM 10% (cap 2 TON)
3. Paste AI creatives from this agent
4. Use their AI rewrite on moderation declines

## C) Telega.io / ton-agent-ads

Use after you know winning angle from official Ads — buy native posts in top USDT/P2P channels for trust lift.
