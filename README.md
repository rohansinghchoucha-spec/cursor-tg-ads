# cursor-tg-ads — AI Telegram Ads for USDT Traders

Bhai, yeh project **USDT / P2P / OTC desk clients** ke liye Telegram pe AI-assisted ads chalane ka brain + dry-run agent hai.

World research: [`docs/WORLD_RESEARCH.md`](docs/WORLD_RESEARCH.md)

## Pehle se kya ready hai (world me)

| Tool | Kaam | Link |
|------|------|------|
| **Telegram Ads (TON)** | Official crypto ads | [ads.telegram.org](https://ads.telegram.org) |
| **ADSLY.pro** | AI copy + IF/THEN auto pause/bid | [adsly.pro](https://adsly.pro) |
| **telegram_ads_mcp** | Cursor/Claude AI agent → ads UI | [GitHub](https://github.com/Free-cat/telegram_ads_mcp) |
| **ton-agent-ads** | Channels dhundo + admin negotiate + TON pay | [GitHub](https://github.com/taijased/ton-agent-ads) |
| **tgadsspy** | Competitor creatives spy | [tgadsspy.com](https://tgadsspy.com) |
| **Telega.io** | Native channel posts buy | marketplace (official ads nahi) |

**Truth:** koi bhi tool “clients guarantee” nahi karta. AI creatives + targeting + optimize loop chala sakta hai; close karna offer + trust pe depend karta hai.

## Is repo me kya banaya

1. **Creative brain** — USDT desk copy (EN/HI/ES/AR/RU) + compliance filter (no guaranteed ROI / flash scam language)
2. **Targeting packs** — P2P, local rails (UPI/NGN/ARS…), traders, wallets, remittance
3. **Optimizer** — low CTR pause, high CTR CPM bump + duplicate winner
4. **Dry-run backend** — bina paisa jalaaye plan/launch/optimize simulate
5. **Lead bot** — Telegram `/start` funnel (volume → network → contact → admin notify)
6. **Integration notes** — ADSLY / MCP / Telega wire-up

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export PYTHONPATH=.

# Demo loop (plan → launch dry-run → optimize)
python -m src.agent.main demo --geo IN --lang hi

# Sirf plan + creatives
python -m src.agent.main plan --niche usdt_p2p --geo IN --lang hi --channels "@your_channel"

# World stack guide
python -m src.agent.main stack

# Tests
pytest -q
```

Lead bot:

```bash
# .env me TELEGRAM_BOT_TOKEN + TELEGRAM_ADMIN_CHAT_ID
python -m src.bot.lead_bot
```

## Recommended live stack (hybrid)

1. `config/campaign.json` me brand, offer, **real bot link** daalo  
2. TON cabinet banao + Fragment se fund (yaad: deposit withdraw nahi hota)  
3. Creatives yahan generate karo → ADSLY pe paste / MCP se create  
4. Optimizer rules ADSLY IF/THEN me mirror karo (CTR pause / CPM scale)  
5. Ad CTA → lead bot → admin close  
6. Spy: tgadsspy pe P2P / USDT creatives dekh ke angles copy-mat, seekh lo  

Cursor se full control chahiye ho to `telegram_ads_mcp` connect karo (`auth_state.json` kabhi commit mat karna).

## Commands

```bash
python -m src.agent.main plan|launch|optimize|demo|stack
  --niche usdt_p2p|local_rails|crypto_traders|wallets_onramps|remittance
  --geo IN|NG|AR|MENA
  --lang en|hi|es|ar|ru
  --channels "@ch1,@ch2"
```

## Compliance note

Legitimate buy/sell desk marketing ke liye hai. Guaranteed returns, fake “flash USDT”, ya misleading investment claims intentionally block kiye gaye hain. Apne jurisdiction ke ads/finance rules khud check karo.
