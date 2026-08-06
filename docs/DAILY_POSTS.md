# Daily auto-post + VE channel targets

## Live channel
- `@p2pupdatescheck` — USDT P2P Venezuela
- Bot: `@Rohanmcpbot`

## What runs automatically
1. `src/bot/daily_poster.py` — picks rotating Spanish post, generates PNG + short MP4, sends photo (+ video)
2. Cron (13:00 UTC ≈ 09:00 Caracas) via `scripts/install_daily_cron.sh`
3. Backup loop: `scripts/daily_scheduler_loop.sh` in tmux `ve-daily-poster`

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
