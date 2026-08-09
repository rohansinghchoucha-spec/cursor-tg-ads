# User MCP (Telethon) — channel post / manage

## Why this path
User MCP = tumhara Telegram account jaise app me. Channel pe post/edit/delete/pin easy.
Package: **mcp-telegram** (`dryeab/mcp-telegram`) via `uv tool install`.

## What AI can do after login
- `send_message` → channel/group/user pe post (text/file)
- `edit_message` / `delete_message`
- `get_messages` / `search_dialogs`
- drafts + media download

## One-time setup

### 1) API ID + Hash
1. https://my.telegram.org/apps
2. Login with phone
3. Create app if needed → copy **api_id** + **api_hash**

### 2) Login session
```bash
export PATH="$HOME/.local/bin:$PATH"
export API_ID=...
export API_HASH=...
export PHONE=+447436763940
# optional if you already have code:
# export CODE=12345
./scripts/mcp_telegram_login.sh
# If script prints WAITING_FOR_CODE:
echo 12345 > /tmp/tg_mcp_code.txt
```

Session file: `~/.local/state/mcp-telegram/session.session` (gitignored / never commit)

### 3) Cursor MCP
`.cursor/mcp.json` me `mcp-telegram` server (API_ID + API_HASH env). Reload MCP.

```json
"mcp-telegram": {
  "command": "/home/ubuntu/.local/bin/mcp-telegram",
  "args": ["start"],
  "env": {
    "API_ID": "...",
    "API_HASH": "..."
  }
}
```

## Cursor prompts (after login)
- “mere channels list karo (`search_dialogs`)”
- “@mychannel pe ye post bhejo…”
- “last post edit/delete karo”

## Safety
- Session = full account access. Share mat karna.
- Sirf apne channels / jahan admin ho.
- Telegram ToS follow karo (spam/mass abuse se account risk).
