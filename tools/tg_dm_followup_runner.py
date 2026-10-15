#!/usr/bin/env python3
"""Private-chat USDT follow-ups until queue empty. Oldest first. Telegram Web via CDP only."""
from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from pathlib import Path

import websocket

QUEUE = Path("/tmp/tg-send-queue.json")
LOG = Path("/tmp/tg-followup-log.jsonl")
STATUS = Path("/tmp/tg-followup-status.txt")
DONE = Path("/tmp/tg-followup-done.json")
HEARTBEAT = Path("/tmp/tg-followup-heartbeat.txt")

LINES = [
    "Sir, do you want to sell USDT?",
    "Sir, abhi bhi USDT bechna hai? Amount bata do.",
    "Hello sir, USDT sell karna ho to amount likh dena.",
    "Sir, do you still want to sell USDT? Kitna bechoge.",
    "Sir, USDT cashout chahiye to amount aur network bata dena.",
]

FLOOD_SLEEP_SEC = 30 * 60
GAP_MIN, GAP_MAX = 42, 68
TRANSIENT_RETRIES = 5


def load_done() -> set[str]:
    done: set[str] = set()
    if DONE.exists():
        try:
            done.update(str(x) for x in json.loads(DONE.read_text()))
        except json.JSONDecodeError:
            pass
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("ok") or r.get("skip"):
                done.add(str(r["peer"]))
    return done


def save_done(done: set[str]) -> None:
    DONE.write_text(json.dumps(sorted(done)))
    DONE.chmod(0o600)


def status(text: str) -> None:
    STATUS.write_text(text + "\n")
    HEARTBEAT.write_text(str(int(time.time())) + "\n")
    print(text, flush=True)


def cdp_call():
    pages = json.load(urllib.request.urlopen("http://127.0.0.1:9333/json/list", timeout=15))
    pg = next(p for p in pages if p.get("type") == "page" and "web.telegram.org" in p.get("url", ""))
    ws = websocket.create_connection(pg["webSocketDebuggerUrl"], timeout=60)
    seq = {"n": 0}

    def call(method, params=None):
        seq["n"] += 1
        ws.send(json.dumps({"id": seq["n"], "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == seq["n"]:
                return msg

    call.close = ws.close  # type: ignore[attr-defined]
    call("Runtime.enable")
    return call


def ev(call, expr: str) -> str:
    r = call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    err = r.get("result", {}).get("exceptionDetails")
    if err:
        exc = err.get("exception") or {}
        desc = exc.get("description") or err.get("text") or "error"
        raise RuntimeError(str(desc)[:400])
    val = r["result"]["result"].get("value")
    if val is None:
        return ""
    return val


def is_flood(msg: str) -> bool:
    low = msg.lower()
    return any(k in low for k in ("flood", "peer_flood", "too many", "spamreport", "limited"))


def send_one(peer: str, line: str) -> None:
    call = cdp_call()
    try:
        ev(
            call,
            """
(async () => {
  const m = await rootScope.managers;
  await m.appMessagesManager.sendText({peerId: %s, text: %s, clearDraft: true});
  return "ok";
})()
"""
            % (json.dumps(peer), json.dumps(line)),
        )
    finally:
        call.close()  # type: ignore[attr-defined]


def main() -> None:
    if not QUEUE.exists():
        status("ERROR no queue at " + str(QUEUE))
        return

    queue = json.loads(QUEUE.read_text())
    done = load_done()
    save_done(done)

    total = len(queue)
    sent_this_run = 0

    for i, row in enumerate(queue):
        peer = str(row["peerId"])
        name = row.get("name") or peer

        if peer in done:
            continue

        line = LINES[i % len(LINES)]
        if (row.get("text") or "").strip() == line:
            line = LINES[(i + 1) % len(LINES)]

        remaining = total - len(done)
        status(f"working remaining={remaining} next={name[:40]}")

        for attempt in range(1, TRANSIENT_RETRIES + 1):
            try:
                send_one(peer, line)
                done.add(peer)
                save_done(done)
                sent_this_run += 1
                LOG.open("a").write(
                    json.dumps({"peer": peer, "name": name, "ok": True, "line": line}) + "\n"
                )
                status(f"sent {len(done)}/{total} {name}")
                break
            except (urllib.error.URLError, websocket.WebSocketException, ConnectionError, TimeoutError) as e:
                wait = min(30, 5 * attempt)
                status(f"retry {attempt}/{TRANSIENT_RETRIES} {name}: network {e!s:.80} sleep {wait}s")
                time.sleep(wait)
            except RuntimeError as e:
                msg = str(e)
                LOG.open("a").write(json.dumps({"peer": peer, "name": name, "err": msg}) + "\n")
                if is_flood(msg):
                    status(f"FLOOD pause 30m at {name}. done={len(done)}/{total}")
                    time.sleep(FLOOD_SLEEP_SEC)
                    attempt -= 1
                    continue
                if attempt < TRANSIENT_RETRIES:
                    wait = 8 * attempt
                    status(f"retry {attempt}/{TRANSIENT_RETRIES} {name}: {msg[:100]} sleep {wait}s")
                    time.sleep(wait)
                    continue
                status(f"skip after errors {name}: {msg[:120]}")
                done.add(peer)
                save_done(done)
                LOG.open("a").write(json.dumps({"peer": peer, "name": name, "skip": "error", "err": msg}) + "\n")
                break
        else:
            status(f"FAILED give up one chat {name}; will retry next outer loop")
            return

        time.sleep(random.randint(GAP_MIN, GAP_MAX))

    status(f"DONE all {total} handled ok+log={len(done)}")


if __name__ == "__main__":
    main()
