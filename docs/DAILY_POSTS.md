# Daily auto-post + VE channel targets

## Live channel
- `@p2pupdatescheck` — USDT P2P Venezuela
- Bot: `@Rohanmcpbot`

## Why posts stopped (important)
Pehle Cloud Agent VM pe `cron` + `tmux` lagaya gaya tha. **Woh VM temporary hoti hai** — agent session band / expire hone ke baad cron/tmux mar jate hain. Isliye “daily maintain” chalna band ho gaya.

**Durable schedule ab GitHub Actions pe hai:**
[`.github/workflows/daily-channel-post.yml`](../.github/workflows/daily-channel-post.yml) — har din **13:00 UTC (~09:00 Caracas)**.

### Enable checklist
1. Merge this branch / PR to `main` (ya Actions ko is branch pe allow karo)
2. Repo → **Settings → Secrets and variables → Actions** me add karo:
   - `TELEGRAM_BOT_TOKEN` (BotFather → `@Rohanmcpbot`)
   - optional `TELEGRAM_CHANNEL` = `@p2pupdatescheck`
3. **Actions → Daily Telegram channel post → Run workflow** se ek baar manual test

Cursor Automations bhi use kar sakte ho (daily scheduled agent) — lekin is repo me durable runner GitHub Actions hai.

## What runs automatically
1. `src/bot/daily_poster.py` — rotating Spanish post + PNG (+ short MP4)
2. **GitHub Actions cron** (primary, durable)
3. Local helpers (dev / one-off only — **not durable on Cloud Agent VMs**):
   - `scripts/install_daily_cron.sh`
   - `scripts/daily_scheduler_loop.sh` (tmux `ve-daily-poster`)

Manual test:
```bash
export PYTHONPATH=.
python -m src.bot.daily_poster --id trust_escrow
```

## Content rotation (7 days)
trust_escrow → pago_movil → trust_wallet → tasa_vs_binance → scams → trc20 → sell_order

Config: `config/daily_posts.json`  
Targets for ads: `config/ve_target_channels.json`

## Ads target channels (research list)
Priority: `@monitorvenezuela`, `@DolarBCV`, `@monitordolarparalelovenezuela`, `@MonitorDolarVeOFICIAL`, `@RadarEconomicoVzla`, `@e_positivo`, …

Verify each is still public before buying ads. Do not spoof their brands.
