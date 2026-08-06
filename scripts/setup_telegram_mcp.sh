#!/usr/bin/env bash
# One-shot setup for Telegram Ads MCP (install already done in tools/)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCP="$ROOT/tools/telegram_ads_mcp"
AUTH_DIR="$HOME/.config/telegram-ads-mcp"
mkdir -p "$AUTH_DIR" "$ROOT/.cursor"

if [[ ! -x "$MCP/.venv/bin/telegram-ads-mcp" ]]; then
  python3 -m venv "$MCP/.venv"
  # shellcheck disable=SC1091
  source "$MCP/.venv/bin/activate"
  pip install -e "$MCP"
  playwright install chromium
fi

cat > "$ROOT/.cursor/mcp.json" <<EOF
{
  "mcpServers": {
    "telegram-ads": {
      "command": "$MCP/.venv/bin/telegram-ads-mcp",
      "env": {
        "TELEGRAM_ADS_AUTH_STATE": "$AUTH_DIR/auth_state.json"
      }
    }
  }
}
EOF

echo "MCP config → $ROOT/.cursor/mcp.json"
echo "Login (browser):"
echo "  cd $ROOT && PYTHONPATH=$MCP/src $MCP/.venv/bin/python scripts/telegram_ads_login.py"
echo "After SUCCESS, reload Cursor MCP servers."
