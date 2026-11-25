# Handoff — dusre Cursor ID / Pro pe yahi kaam continue

**Updated:** 2026-11-25 21:10 IST  
**Source chat:** Cloud Agent `bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789`  
**URL (sirf us account pe):** https://cursor.com/agents/bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789  
**Owner email (purana Cursor):** `rohansinghchoucha@gmail.com`  
**Full transcript (git):** `memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md`  
**Restore steps:** `memory/RESTORE_ON_NEW_CURSOR.md`  
**Ops snapshot (live ads state):** `memory/OPS_SNAPSHOT.md`

Naya Cursor account / naya agent: pehle yeh padho, phir `AGENTS.md` + `memory/CHANNEL_RESEARCH.md` + `memory/channels.json` + transcript.

---

## 0) Seedhi baat — ID change pe kya milta hai

| Cheez | Git pe? | Dusre Cursor pe |
|---|---|---|
| Poori channel research + DROP/KEEP | Haan | Clone repo → mil jayega |
| Ad IDs, budgets, winners, CPM rules | Haan | Same |
| Poora chat transcript (sanitized) | Haan | Padh sakta hai / naya agent ko de |
| Rules + channel-hunt skill | Haan (`.cursor/`) | Repo open pe apply |
| Tools (`tg_audit.py` etc.) | Haan | Same |
| Telegram Ads **2FA password**, cookies, API keys | **Nahi** (jaanna chahiye) | Password manager / `local/` copy alag se |
| Cloud Agent chat URL | Account-scoped | Alag personal Pro pe nahi khulegi unless same Team |

**Rule:** Cursor cloud chat move nahi hoti. Business memory **GitHub repo** pe locked hai. Secrets **kabhi git mein mat daalo**.

---

## 1) Jo Git pe HAI (dusre Cursor ko milega)

| Path | Kya hai |
|---|---|
| `AGENTS.md` | Business rules, rate rule, research method |
| `memory/CHANNEL_RESEARCH.md` | Poori history §0–§126+: DROP, winners, budgets, CPM |
| `memory/channels.json` | Machine-readable channel + campaign log |
| `memory/OPS_SNAPSHOT.md` | Last known live ads cabinet state |
| `memory/RESTORE_ON_NEW_CURSOR.md` | Step-by-step naya ID pe restore |
| `memory/SECRETS.TEMPLATE.env` | Key **names** checklist (values nahi) |
| `memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md` | Full user/assistant transcript |
| `memory/ads-backup-*`, `FINAL-*`, `WAVE*`, `spy_reports.json` | Purane packs / spy dumps |
| `.cursor/rules/`, `.cursor/skills/channel-hunt/` | Agent rules + hunt skill |
| `tools/` | `tg_audit.py`, telemetr helpers, etc. |

**Repo:** `github.com/rohansinghchoucha-spec/cursor-tg-ads`  
**Working branch (memory updates):** `cursor/channel-research-memory-2789` (PR → `main`)

---

## 2) Jo Git pe NAHI jayega (aur nahi jaana chahiye)

| Cheez | Kahan rakhna hai |
|---|---|
| Telegram Ads / Web **2FA password** | Password manager only |
| OTP / confirm-on-Telegram | Live phone |
| Chrome Ads cookies / `stel_*` | gitignored `local/chrome-tg-debug` |
| Telemetr / TGAdsSpy cookies + API keys | gitignored `local/` (`nexa_keys.env`, `telemetr_cookies.json`, `spy_cookies.json`) |
| Fragment wallet seed / private keys | Kabhi git mein mat daalo |

`local/` folder **`.gitignore`** mein hai. Naye machine pe: `memory/SECRETS.TEMPLATE.env` se `local/nexa_keys.env` banao, values password manager se bharo.

Naye Cursor Pro pe: GitHub se repo clone → Ads cabinet alag se `ads.telegram.org` pe phone confirm se login.

---

## 3) Brand / desk (locked)

| Field | Value |
|---|---|
| Brand | Nexa Desk Pay |
| Destination | `t.me/safepathdeals` (rename mat) |
| Support | `@BussinessMen0`, `@nexadeskrates` |
| Users-ad invite (tracking) | `t.me/+hSkyTs1kg_8wMTNk` |
| Audience | Indian USDT **sellers/holders** (1k–10k+ prefer) |
| Offer | We Buy USDT · Min 500 USDT · UPI/Bank live rate |
| Rate rule | Naye/edit ad se pehle newest `TODAY LATEST RATE` on `t.me/s/safepathdeals` vs `t.me/s/nexadeskrates` (newer date). Active ad sirf rate ke liye edit mat karo |
| Ads login phone (cabinet) | `+447436763940` (confirm via Telegram app) |
| Cabinet display name | Rohan Singh |

---

## 4) Ads cabinet — winners as of 2026-11-23 load (§125–§126)

Credit **+60 TON** 23 Nov. Loaded **60** into winners + later **+4** china from spare.

| Ad ID | Title | Role | CPM | Last load | Notes |
|---|---|---|---|---|---|
| **33** | users india apps | Cheapest joins | 1.5 | **+28** | Nov17 slice CPA **0.25** — #1 |
| **28** | quality holders | **xWallet** `linkxwalletnow` + `atgofficiale` | 5 | **+24** | Quality sellers |
| **38** | link diwa reach | `linkpay8` + `diwapay` | 5 | **+8** | Keep small |
| **40** | china ddpay only | **only** `ddpay9999` | 5 | **+4** | First 8 TON CPA **1.14** — small test only |

**Spare after §126:** ~**0.63** TON.

**Mat on / mat refill (unless fresh audit overturns):**  
13, 19 loot, 20 (dead mix), 21 accounts, 22/23/24 wave packs, 29 quality sellers, 30 bulk (mehnga vs users), 31 bulk try 4, 35 search apps.  
Search 36/37 weak. Rate beat **32** naya paisa mat.

CPM/text **edit mat** (Review pe chala jata hai). Budget add = `incrAdBudget` only.

Working CPMs: search **1.50** · channel **5.00** · rate/bulk **7.00** — active CPM mat badlo/ghatana.

---

## 5) Live channels that matter

| Handle | Role |
|---|---|
| `linkxwalletnow` | Best seller source (holders + users) |
| `atgofficiale` | Real ATG with holders |
| `linkpay8` | Hot LinkPay official (ad 38) |
| `diwapay` | Official Diwa (not `diwapay_support_crypto` loot) |
| `ddpay9999` | China lane clean single (ad 40) |
| `acpayschannel`, `MeteorpayEliteChannel00011` | Users + old bulk |
| `glpay21` | Crossed 1k — deferred small-order |

`xwallet7` = affiliate mirror (WATCH). `xwalletcorporate` / cheque under-1k = SKIP.  
DROP education lane. Pakistan no-spend (INR desk).

---

## 6) Dusre Cursor pe pehli message (copy-paste)

```text
Pehle padho (order):
1) memory/RESTORE_ON_NEW_CURSOR.md
2) memory/HANDOFF_OTHER_CURSOR.md
3) AGENTS.md
4) memory/OPS_SNAPSHOT.md
5) memory/CHANNEL_RESEARCH.md (§122–§126+)
6) memory/channels.json
7) memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md (jab deep history chahiye)

Nexa Desk Pay. Dest t.me/safepathdeals. Support @BussinessMen0 @nexadeskrates.
Winners: ad 33 users (+28), ad 28 holders xWallet+ATG (+24), ad 38 link+diwa (+8), ad 40 ddpay only (+4 small).
DROP/DEAD/BLOCK bina fresh live audit ke wapas mat recommend.
Secrets/password/cookies git mein nahi — ads.telegram.org phone +447436763940 se confirm login.
Ab cabinet check karke bata: kaun Active, kitna left, kisko load.
```

---

## 7) Related chats (history)

- Performance (yeh): `bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789`
- Recommend→drop: `bc-9eb05ff1-69f0-4877-b7f2-0cf27bedb69d`
- Activation audit: `bc-fe52cbc5-8e0f-5e18-9b5e-2d0d15df195e`

Cloud Agent chats **account-scoped** hain. Alag personal Pro pe yeh cloud URL khulegi nahi unless same Cursor **Team** + repo access. Isliye yeh git handoff + transcript zaroori hai.
