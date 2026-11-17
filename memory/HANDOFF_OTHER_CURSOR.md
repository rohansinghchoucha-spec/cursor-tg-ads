# Handoff — dusre Cursor Pro pe yahi kaam continue

**Updated:** 2026-11-17 14:35 IST  
**Source chat:** Cloud Agent `bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789`  
**URL (sirf us account pe):** https://cursor.com/agents/bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789  
**Full transcript (git):** `memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md`

Naya Cursor account / naya agent: pehle yeh padho, phir `AGENTS.md` + `memory/CHANNEL_RESEARCH.md` + `memory/channels.json`.

---

## 1) Jo Git pe HAI (dusre Cursor ko milega)

| Path | Kya hai |
|---|---|
| `AGENTS.md` | Business rules, rate rule, research method |
| `memory/CHANNEL_RESEARCH.md` | Poori history §0–§120: DROP lists, winners, budgets, CPM |
| `memory/channels.json` | Machine-readable channel + campaign status |
| `memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md` | Is chat ka poora user/assistant transcript (secrets redacted) |
| `memory/ads-backup-*`, `FINAL-*`, `WAVE*`, `spy_reports.json` | Purane packs / spy dumps |
| `.cursor/rules/`, `.cursor/skills/channel-hunt/` | Agent rules + hunt skill |
| `tools/` | `tg_audit.py`, telemetr helpers, etc. |

**Repo:** `github.com/rohansinghchoucha-spec/cursor-tg-ads`  
**Working branch (memory updates):** `cursor/channel-research-memory-2789` (PR #2 → `main`)

---

## 2) Jo Git pe NAHI jayega (aur nahi jaana chahiye)

| Cheez | Kahan rakhna hai |
|---|---|
| Telegram Ads / Web **2FA password** | Password manager only |
| OTP / confirm-on-Telegram | Live phone |
| Chrome Ads cookies / `stel_*` | gitignored `local/chrome-tg-debug` |
| Telemetr / TGAdsSpy cookies + API keys | gitignored `local/` (`nexa_keys.env`, `telemetr_cookies.json`, `spy_cookies.json`) |
| Fragment wallet seed / private keys | Kabhi git mein mat daalo |

`local/` folder **`.gitignore`** mein hai. Restore pattern (purana VM): `bash local/RESTORE.sh` — sirf us machine pe jahan `local/` copy kiya ho.

Naye Cursor Pro pe: GitHub se repo clone karo. Ads cabinet alag se `ads.telegram.org` pe phone confirm se login. Secrets chat / git mein paste mat karna.

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

---

## 4) Ads cabinet — last known winners (9 Nov 23:16 IST load)

Account display name: **Rohan Singh**. Unallocated after load: **16.63 TON** (40 aaya, 28 use).

| Ad ID | Title | Role | CPM | Last load | Status after load |
|---|---|---|---|---|---|
| **28** | quality holders | **xWallet** `linkxwalletnow` + `atgofficiale` | 5 | +8 | Active — **winner channel** |
| **33** | users india apps | India + china-pay audiences (xWallet etc.) | 1.5 | +12 | Active — **cheapest joins** |
| **38** | link diwa reach | `linkpay8` + `diwapay` only | 5 | +8 | Active |

**Mat on / mat refill (unless fresh audit overturns):**  
13, 19 loot, 20 (dead mix), 21 accounts, 22/23/24 wave packs, 29 quality sellers, 30 bulk (mehnga vs users), 31 bulk try 4, 35 search apps.  
Rate beat **32** pehle se funded — naya paisa mat. Search 36/37 0 joins — refill mat.

CPM/text **edit mat** (Review pe chala jata hai). Budget add = `incrAdBudget` only.

---

## 5) Live channels that matter

| Handle | Role |
|---|---|
| `linkxwalletnow` | Best seller source (holders + users) |
| `atgofficiale` | Real ATG with holders |
| `linkpay8` | Hot LinkPay official (ad 38) |
| `diwapay` | Official Diwa (not `diwapay_support_crypto` loot) |
| `acpayschannel`, `MeteorpayEliteChannel00011` | Users + old bulk |
| `glpay21` | Crossed 1k — deferred, small-order lane, not in last 28 |

DROP education lane (CryptoPointHi, etc.) — mat dohrao. Pakistan no-spend (INR desk).

---

## 6) Dusre Cursor pe pehli message (copy-paste)

```text
Pehle padho: AGENTS.md, memory/HANDOFF_OTHER_CURSOR.md, memory/CHANNEL_RESEARCH.md (§117–§120), memory/channels.json, memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md.
Nexa Desk Pay. Dest t.me/safepathdeals. Support @BussinessMen0 @nexadeskrates.
Winners: ad 28 holders (xWallet+ATG), ad 33 users, ad 38 linkpay8+diwapay.
DROP/DEAD/BLOCK bina fresh live audit ke wapas mat recommend.
Secrets/password/cookies git mein nahi — ads.telegram.org alag login.
Ab cabinet check karke bata: kaun Active, kitna left, kisko load.
```

---

## 7) Related chats (history)

- Performance (yeh): `bc-29fb44ad-c9b1-4dec-9ea5-fb00c0b22789`
- Recommend→drop: `bc-9eb05ff1-69f0-4877-b7f2-0cf27bedb69d`
- Activation audit: `bc-fe52cbc5-8e0f-5e18-9b5e-2d0d15df195e`

Cloud Agent chats **account-scoped** hain. Alag personal Pro pe yeh cloud URL khulegi nahi unless same Cursor **Team** + repo access. Isliye yeh git handoff + transcript zaroori hai.
