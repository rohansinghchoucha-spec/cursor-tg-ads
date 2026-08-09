#!/usr/bin/env bash
# Posts once per local Caracas day at ~09:00 (UTC-4 => 13:00 UTC)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT"
MARKER="$ROOT/data/posts/last_day.txt"
LOG="$ROOT/data/posts/scheduler.log"
mkdir -p "$ROOT/data/posts"
cd "$ROOT"
while true; do
  # Caracas day key approx UTC-4
  DAY=$(TZ=America/Caracas date +%F)
  HOUR=$(TZ=America/Caracas date +%H)
  if [[ "$HOUR" == "09" ]]; then
    LAST=$(cat "$MARKER" 2>/dev/null || true)
    if [[ "$LAST" != "$DAY" ]]; then
      echo "$(date -u +%FT%TZ) posting for $DAY" >>"$LOG"
      source "$ROOT/.venv/bin/activate"
      set -a; source <(grep -E '^(TELEGRAM_BOT_TOKEN|TELEGRAM_CHANNEL)=' "$ROOT/.env"); set +a
      python -m src.bot.daily_poster >>"$LOG" 2>&1 && echo "$DAY" >"$MARKER"
    fi
  fi
  sleep 300
done
