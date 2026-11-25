# Naya Cursor ID pe restore (checklist)

**Updated:** 2026-11-25 21:10 IST

Cloud Agent chat naye personal Cursor Pro pe auto-transfer **nahi** hoti. Jo GitHub pe hai, wahi portable memory hai.

## A) Purane account pe (logout se pehle)

1. Confirm latest push: branch `cursor/channel-research-memory-2789` (ya `main` agar merge ho chuka).
2. Confirm ye files latest hain:
   - `memory/CHANNEL_RESEARCH.md`
   - `memory/channels.json`
   - `memory/HANDOFF_OTHER_CURSOR.md`
   - `memory/OPS_SNAPSHOT.md`
   - `memory/chat-transcripts/TELEGRAM_AD_PERFORMANCE_bc-29fb44ad.md`
3. Secrets alag backup (USB / password manager / encrypted note):
   - Telegram Ads 2FA password
   - Telemetr / TGAdsSpy cookies ya API keys (agar use karte ho)
   - Koi wallet seed — sirf offline, kabhi chat/git nahi
4. Optional: `local/` folder (agar VM pe tha) zip karke private rakh — git mein mat.

## B) Naye Cursor account pe

1. Naye Pro se login.
2. GitHub connect: same repo `rohansinghchoucha-spec/cursor-tg-ads` (invite/collab agar alag GitHub user).
3. Repo clone / Cloud Agent usi repo pe start.
4. Branch: pehle `cursor/channel-research-memory-2789` (latest memory) ya `main` after merge.
5. Naye agent ko pehli message: `HANDOFF_OTHER_CURSOR.md` §6 wala copy-paste block.
6. Ads: `ads.telegram.org` → phone `+447436763940` → Telegram app pe **Confirm access**.
7. Secrets: `memory/SECRETS.TEMPLATE.env` copy → `local/nexa_keys.env` (gitignored) → values bharo.

## C) Verify (naya agent yeh check kare)

- [ ] `AGENTS.md` padha
- [ ] `memory/CHANNEL_RESEARCH.md` last § (126+) padha
- [ ] Cabinet: Ad 28 / 33 / 38 / 40 status + left budget
- [ ] DROP list respect
- [ ] Rate rule: naye ad se pehle `safepathdeals` / `nexadeskrates` latest rate

## D) Jo expect mat karo

- Purani cloud chat URL naye personal account pe list mein aana (unless same Team).
- Chrome Ads session cookies git se restore (hamesha fresh login).
- 2FA password git se milna — woh intentionally git pe nahi hai.
