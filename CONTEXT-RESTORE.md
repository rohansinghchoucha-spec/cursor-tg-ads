# Context Restore Guide (Cursor ID / machine change)

Yeh repo **source of truth** hai. Agar Cursor account / ID change ho, naya login ho, ya naya machine pe git connect ho — pehle yeh files padho. Chat transcript cloud pe depend mat karo.

## Restore order (5 min)

1. `README.md` — map of all docs  
2. `TELEGRAM-MAX-VOLUME-ADS-PLAYBOOK.md` — Telegram max-volume ads research (Nov 2026)  
3. `docs/channel-audits/TimeDealsOfficial.md` — channel journey + audits + current gaps  
4. `docs/research/india-phone-seller-ads.md` — India seller/booking channels with TG Ads  
5. `docs/policy/telegram-ads-compliance-deals.md` — policy rules for rates/cheap claims  
6. `docs/action-plans/exact-post-changes.md` — exact edit/delete/pin checklist  

## What is saved here

| Content | Where |
|---|---|
| Official / Telega / bot / syndicate playbook | `TELEGRAM-MAX-VOLUME-ADS-PLAYBOOK.md` |
| Web research links + benchmarks | playbook + research docs |
| `@Time_Carder_Store` → `@TimeDealsOfficial` history | `docs/channel-audits/` |
| Post-by-post audits (multiple dates) | same |
| India booking/seller advertisers list | `docs/research/` |
| TG Ads policy keep/remove rules | `docs/policy/` |
| Exact copy-paste post templates | `docs/action-plans/` |
| Two-AI advice diff summary | `docs/action-plans/advice-diff-merge.md` |

## What git does NOT store

- Live Telegram private chats / unpublished drafts  
- Cursor cloud chat UI history (may not move with account)  
- Ad account balances / Fragment wallet  

Unke liye repo docs hi portable backup hain.

## New Cursor ID setup

```bash
git clone https://github.com/rohansinghchoucha-spec/cursor-tg-ads.git
cd cursor-tg-ads
# open folder in Cursor → read CONTEXT-RESTORE.md first
```

Branch with full work: `cursor/telegram-max-volume-ads-playbook-7f62`  
Or merge to `main` after PR approval.

## Last context snapshot

- Channel: https://t.me/TimeDealsOfficial (`Time Deals Store`)  
- Goal: genuine deals channel + Official Telegram Ads ready  
- Hard policy wording (carder/cheap-dream-hurry): cleared in audits  
- Remaining soft gaps: media-only captions, re-pin rate list, return policy, exact model names  
- Research cutoff for playbook: 16 Nov 2026; channel audits through 25 Nov 2026
