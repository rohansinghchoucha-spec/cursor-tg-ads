---
name: channel-hunt
description: Find Telegram Ads target channels for Nexa Desk Pay Indian USDT sellers. Use when hunting, recommending, or dropping channels, or when the user asks for MCP/skills/tools to discover targeting inventory.
---

# Channel hunt (Nexa Desk Pay)

Audience = Indian **USDT sellers/holders** who want INR cashout. China-pay/gaming apps allowed. Not education, loot, flash USDT, forex, mule-recruit.

Always read `memory/CHANNEL_RESEARCH.md` + `memory/channels.json` first. Do not re-recommend `DROP`/`DEAD`/`BLOCK` without a fresh live audit that overturns the reason.

## What actually finds Ads-target channels

Telegram Ads can only target **public channels**. Groups/restricted previews are useless.

Ranked methods (use in this order):

1. **Competitor creatives → CTA dest** (not their cheap placements)
   - CLI: `python3 tools/spy_pro.py ads --q USDT --geo IN --limit 20`
   - No key: `https://telemetr.com/api/v1/ads?q=USDT&geo=IN&limit=20` (G.Media, same archive as TGAdsSpy, plan ANON)
   - Keep the **destination** `@handle` only if live `t.me/s` shows seller/app-rate posts.
   - Do **not** copy “where the ad was shown” from keyword spray (sports/loot/wallpaper). That shelf already failed.

2. **Official china-pay app catalog**
   - `python3 tools/telemetr_search.py diwapay linkpay ezpay 999pay umoney zkpay`
   - Then `python3 tools/tg_audit.py <handle>`
   - Prefer Ads-eligible (`isSponsoredEligible`) + members ≥1k + recent posts + median views not dead.

3. **Mention snowball from winners**
   - `python3 tools/discover_mentions.py diwapay linkpay8 wallet_999pay ezpay_rogen zkpay108`
   - Most hits are CS bots. Keep only new **official app** channels.

4. **Live preview is the judge**
   - `python3 tools/tg_audit.py handle`
   - Need: last post ≤7d, median views meaningful vs members, copy = USDT sell / UPI rate / app orders — not invite-bonus, PhonePe unblock, bank-account recruit.

## MCP / extra products (web-checked 2026-10-03)

| Thing | Use? | Why |
|---|---|---|
| Cursor built-in Telegram skill | No | Does not exist |
| `telemetr.com` / TGAdsSpy public API | **Yes, already** | Same G.Media archive. ANON works without Pro. Buy-map still Enterprise $499 |
| TGAdsSpy / Telemetr.io **PRO/Advanced renew** | Yes if budget | Deep page + Ads Index. Does **not** open a new whale class |
| [TGStat MCP](https://github.com/theyahia/tgstat-mcp) | Later only | Needs `TGSTAT_TOKEN` (paid Stat/Search API, RUB). India catalog exists (`in.tgstat.com`) but default = education megas. Cloud IP often 403 |
| [Telemetr.me MCP](https://mcp.telemetr.me/) | Skip | Different product from telemetr.io; catalog MCP, no Ads buy-map |
| [telegram_ads_mcp](https://github.com/Free-cat/telegram_ads_mcp) | Ads ops only | Drives `ads.telegram.org`. Does **not** discover channels |
| Telega.in / Tagio | Skip for this goal | Native **post buy**, not Telegram Ads targeting |
| Lyzem (`tools/tg_discover.py`) | Weak | Public index; mostly wrong geo / loot / education |

Do not install random scrapers. Extra dumps without live audit = loot/signals.

## After any hunt

Update `memory/CHANNEL_RESEARCH.md` + `memory/channels.json` same turn. Prefer leftover TEST (`zkpay108`, `tamilp2pusdt`) over inventing an 8-pack. Never pad with Jaipay/LG-dead/WYpay/gambling.
