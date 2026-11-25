#!/usr/bin/env bash
# Run until /tmp/tg-followup-status.txt contains DONE or queue fully logged.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/tools/tg_dm_followup_runner.py"
QUEUE="/tmp/tg-send-queue.json"
STATUS="/tmp/tg-followup-status.txt"

ensure_chrome() {
  if curl -sf http://127.0.0.1:9333/json/version >/dev/null 2>&1; then
    return 0
  fi
  mkdir -p /tmp/chrome-tg-debug
  google-chrome --remote-debugging-port=9333 --remote-allow-origins=* \
    --user-data-dir=/tmp/chrome-tg-debug --no-first-run --no-default-browser-check \
    --disable-dev-shm-usage --window-size=1280,900 "https://web.telegram.org/k/" \
    >/tmp/chrome-tg-followup.log 2>&1 &
  for _ in $(seq 1 30); do
    sleep 2
    curl -sf http://127.0.0.1:9333/json/version >/dev/null 2>&1 && return 0
  done
  echo "chrome failed" >> "$STATUS"
  return 1
}

count_done() {
  python3 - <<'PY'
import json
from pathlib import Path
done=set()
p=Path("/tmp/tg-followup-done.json")
if p.exists():
    try:
        done.update(str(x) for x in json.loads(p.read_text()))
    except Exception:
        pass
for line in Path("/tmp/tg-followup-log.jsonl").read_text().splitlines() if Path("/tmp/tg-followup-log.jsonl").exists() else []:
    try:
        r=json.loads(line)
    except Exception:
        continue
    if r.get("ok") or r.get("skip"):
        done.add(str(r["peer"]))
q=len(json.loads(Path("/tmp/tg-send-queue.json").read_text()))
print(len(done), q)
PY
}

while true; do
  if [[ ! -f "$QUEUE" ]]; then
    echo "no queue" > "$STATUS"
    sleep 120
    continue
  fi
  read -r DONE_COUNT TOTAL <<< "$(count_done)"
  if [[ "$DONE_COUNT" -ge "$TOTAL" ]]; then
    echo "DONE all $TOTAL handled" > "$STATUS"
    exit 0
  fi
  if grep -q "^DONE" "$STATUS" 2>/dev/null; then
    exit 0
  fi
  ensure_chrome || { sleep 60; continue; }
  python3 "$PY" || true
  read -r DONE_COUNT TOTAL <<< "$(count_done)"
  if [[ "$DONE_COUNT" -ge "$TOTAL" ]]; then
    echo "DONE all $TOTAL handled" > "$STATUS"
    exit 0
  fi
  echo "loop sleep 30s done=$DONE_COUNT/$TOTAL" >> "$STATUS"
  sleep 30
done
