#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=.
CHAT="${TELEGRAM_CHANNEL:-@p2pupdatescheck}"
TEXT=${1:-"Actualización: el canal se mantiene activo. Pronto publicamos el enlace oficial de la DApp en Trust Wallet. Opera con cuidado — no es asesoría financiera."}
python3 -m src.bot.channel_poster post --chat "$CHAT" --text "$TEXT"
