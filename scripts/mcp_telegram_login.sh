#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
TOOL_PY="$(find "$HOME/.local/share/uv/tools" -path '*mcp-telegram*/bin/python' | head -1)"
: "${TOOL_PY:?mcp-telegram tool python not found}"
: "${API_ID:?Set API_ID}"
: "${API_HASH:?Set API_HASH}"
: "${PHONE:?Set PHONE}"
export CODE_FILE="${CODE_FILE:-/tmp/tg_mcp_code.txt}"
export PASS_FILE="${PASS_FILE:-/tmp/tg_mcp_2fa.txt}"
exec "$TOOL_PY" - <<'PY'
import asyncio, os, time
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from xdg_base_dirs import xdg_state_home

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
phone = os.environ["PHONE"]
code_file = Path(os.environ.get("CODE_FILE", "/tmp/tg_mcp_code.txt"))
pass_file = Path(os.environ.get("PASS_FILE", "/tmp/tg_mcp_2fa.txt"))
state = Path(xdg_state_home()) / "mcp-telegram"
state.mkdir(parents=True, exist_ok=True)
session = state / "session"
client = TelegramClient(str(session), api_id, api_hash)

def wait_file(path: Path, label: str, timeout=600) -> str:
    print(f"WAITING_FOR_{label}: echo CODE > {path}", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists():
            val = path.read_text().strip()
            if val:
                path.unlink(missing_ok=True)
                return val
        time.sleep(1)
    raise TimeoutError(label)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        code = os.environ.get("CODE") or wait_file(code_file, "CODE")
        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            pw = os.environ.get("PASSWORD") or wait_file(pass_file, "2FA")
            await client.sign_in(password=pw)
    me = await client.get_me()
    print(f"SUCCESS user={me.first_name} id={me.id} username={getattr(me,'username',None)}", flush=True)
    env_path = state / "credentials.env"
    env_path.write_text(f"API_ID={api_id}\nAPI_HASH={api_hash}\n")
    os.chmod(env_path, 0o600)
    print(f"CREDENTIALS_SAVED {env_path}", flush=True)
    await client.disconnect()

asyncio.run(main())
PY
