# Channel bot (@Rohanmcpbot)

## Setup checklist
1. BotFather → bot created (done)
2. Channel → Administrators → Add Admin → **@Rohanmcpbot**
3. Enable at least: **Post Messages** (also Edit/Delete if needed)
4. Save
5. Run discover OR send channel `@username` to agent

## Commands
```bash
export PYTHONPATH=.
python -m src.bot.channel_poster me
python -m src.bot.channel_poster discover --wait 300
python -m src.bot.channel_poster post --chat @your_channel --text "Hello from MCP"
```

Token lives in `.env` as `TELEGRAM_BOT_TOKEN` (never commit).

## Important
Public channel `@username` pe `getChat` succeed ho sakta hai bina membership ke.
Post ke liye bot **real admin member** hona zaroori hai.
