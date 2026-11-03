#!/usr/bin/env python3
"""Join Nexa quality-ad placement channels via Telegram Web CDP."""
import json
import time
import urllib.request
import websocket

CHANNELS = [
    "linkxwalletnow",
    "atgofficiale",
    "TF_Exchange",
    "bhaartpay",
    "quickpayoffical1",
]


def cdp():
    pages = json.load(urllib.request.urlopen("http://127.0.0.1:9333/json/list", timeout=15))
    pg = next(p for p in pages if p.get("type") == "page" and "web.telegram.org" in p.get("url", ""))
    ws = websocket.create_connection(pg["webSocketDebuggerUrl"], timeout=60)
    n = {"i": 0}

    def call(method, params=None):
        n["i"] += 1
        ws.send(json.dumps({"id": n["i"], "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == n["i"]:
                return msg

    call.close = ws.close  # type: ignore[attr-defined]
    call("Runtime.enable")
    return call


def ev(call, expr):
    r = call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    err = r.get("result", {}).get("exceptionDetails")
    if err:
        exc = err.get("exception") or {}
        raise RuntimeError(str(exc.get("description") or err.get("text"))[:400])
    return r["result"]["result"].get("value")


def main():
    call = cdp()
    try:
        me = ev(
            call,
            """(async () => {
              const m = await rootScope.managers;
              const u = await m.appUsersManager.getSelf();
              return JSON.stringify({user: u.username, id: u.id});
            })()""",
        )
        print("logged_in", me)
        results = []
        for handle in CHANNELS:
            expr = """
(async () => {
  const m = await rootScope.managers;
  const handle = %s;
    try {
    const chat = await m.appUsersManager.resolveUsername(handle);
    if (chat.pFlags && chat.pFlags.left) {
      await m.appChatsManager.joinChannel(chat.id);
    }
    const again = await m.appUsersManager.resolveUsername(handle);
    return JSON.stringify({handle, title: again.title || handle, joined: !(again.pFlags && again.pFlags.left), ok: true});
  } catch (e) {
    return JSON.stringify({handle, ok: false, err: String(e).slice(0, 200)});
  }
})()
""" % json.dumps(handle)
            out = ev(call, expr)
            results.append(json.loads(out))
            print(out)
            time.sleep(2)
        open("/tmp/tg-join-ad-channels.json", "w").write(json.dumps(results, indent=2))
    finally:
        call.close()  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
