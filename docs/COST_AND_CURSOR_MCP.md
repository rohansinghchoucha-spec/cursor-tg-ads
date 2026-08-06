# Telegram Ads cost + Cursor MCP — kaise AI chalega

## 1) Kitna kharcha (TON cabinet — USDT desk ke liye recommended)

| Item | Approx |
|------|--------|
| Pehla deposit (Fragment) | **~20 TON ≈ $50–60** (withdraw nahi hota) |
| Min CPM (floor) | **0.1 TON ≈ $0.35–0.50** / 1000 views |
| Real crypto niche CPM | aksar **$2–15** / 1000 (competition pe) |
| Soft test budget | **$50–150** (1–2 hafte signals) |
| Serious test | **$300–800 / month** |
| Scale (jab CPA clear) | **$1k–5k+ / month** |

**Rough math:**  
CPM $5 pe $100 ≈ 20,000 impressions. CTR 1% ≈ 200 clicks. Bot pe 10–20% lead = 20–40 leads. Desk close rate alag.

**Extra (optional):**
- ADSLY automation SaaS: ~$129–229/mo (MCP free alternative)
- Telega/KOL native posts: per channel deal (alag budget)
- MCP khud: **free open-source**, sirf ad spend + laptop/server

**Stars cabinet:** chhota test / soft moderation — alag pricing (Stars).  
**Euro cabinet:** usually reseller + bada minimum (€1.5k–3k) — pehle mat.

---

## 2) MCP hai kya?

Haan. Official Telegram Ads public REST API nahi deta.  
**MCP = Model Context Protocol** — Cursor ke andar tools plug karne ka tarika.

Repo: https://github.com/Free-cat/telegram_ads_mcp

Ye MCP Playwright se `ads.telegram.org` kholta hai (tumhari saved login session se) aur AI ko tools deta hai:

| Tool | Kaam |
|------|------|
| `list_accounts` / `list_ads` | campaigns dekhna |
| `create_ad` | naya ad banana |
| `set_cpm` / `set_budget` / `increase_budget` | bid/budget |
| `set_status` | Active / On Hold |
| `get_ad_stats_csv` | performance download |
| `update_ad` | copy update |

Write/spend tools pehle `confirm=False` (dry-run), phir `confirm=True`.

⚠️ `auth_state.json` = tumhara ads login. Kabhi git me mat daalna.

---

## 3) Cursor kaise AI se ads chalayega (step-by-step)

```
Tum Cursor me bolte ho
        ↓
Cursor Agent (LLM)
        ↓
MCP tools (telegram_ads_mcp)
        ↓
ads.telegram.org (real cabinet)
        ↓
Telegram channels pe sponsored ads
        ↓
CTA → tumhara lead bot → client
```

### Setup (ek baar)

1. TON Ads account banao → Fragment se ~20 TON fund  
2. Clone `telegram_ads_mcp` → Playwright se ek baar login → `auth_state.json` save  
3. Cursor Settings → MCP → server add (command + AUTH_STATE_PATH)  
4. Is repo me `config/campaign.json` me brand + real bot link daalo  

### Daily / weekly flow (Cursor chat me)

1. **Plan:** “IN geo ke liye USDT P2P ads banao, UPI hook, 4 creatives”  
   - Agent is repo se / LLM se copy + channel list nikalta hai  
2. **Create dry-run:** MCP `create_ad` with `confirm=False` → preview check  
3. **Go live:** `confirm=True` → paisa lagega  
4. **Optimize:** “stats nikaalo, CTR < 0.25% pause, winners pe CPM +10%”  
   - Agent `get_ad_stats_csv` → `set_status` / `set_cpm`  
5. **Moderation fail:** AI copy rewrite → resubmit  

Tumhari job: budget cap, offer truth, final `confirm=True` approve.  
AI ki job: copy, targeting list, create, pause, scale.

### Cursor me example prompts

```
List my Telegram Ads accounts and active ads via MCP.
```

```
Create a TON ad for USDT desk targeting these channels: @ch1 @ch2
Title/text from our plan. Dry-run first (confirm=false).
```

```
Download stats for ad X last 24h. If CTR < 0.25% after 5k impressions, pause it.
If CTR > 1.2%, raise CPM by 10% (confirm=false first).
```

---

## 4) Do raaste (choose)

| Path | Cost | AI auto level |
|------|------|----------------|
| **Cursor + MCP** | Ad spend only | High (tum chat se control) |
| **ADSLY** | Ad spend + ~$129/mo | Highest hands-off IF/THEN |
| **Hybrid** | dono | ADSLY 24/7 rules + Cursor deep ops |

Beginner tip: pehle **$50–100 TON test + Cursor MCP dry-run**, phir scale.
