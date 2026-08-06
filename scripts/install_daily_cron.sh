#!/usr/bin/env bash
# Install / refresh daily cron for VE channel auto-posts (America/Caracas ~09:00)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
LOG="$ROOT/data/posts/cron.log"
mkdir -p "$ROOT/data/posts"

# Caracas is UTC-4 → 09:00 local ≈ 13:00 UTC
CRON_LINE="0 13 * * * cd $ROOT && PYTHONPATH=$ROOT TELEGRAM_BOT_TOKEN=\$(grep ^TELEGRAM_BOT_TOKEN= $ROOT/.env | cut -d= -f2-) TELEGRAM_CHANNEL=@p2pupdatescheck $PY -m src.bot.daily_poster >> $LOG 2>&1"

# Keep other crontab lines; replace our marker
TMP=$(mktemp)
crontab -l 2>/dev/null | grep -v 'src.bot.daily_poster' >"$TMP" || true
echo "$CRON_LINE" >>"$TMP"
crontab "$TMP"
rm -f "$TMP"
echo "Installed cron:"
crontab -l | grep daily_poster || true
echo "Log: $LOG"
