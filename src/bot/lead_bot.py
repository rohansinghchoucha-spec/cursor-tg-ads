"""Telegram lead qualification bot for USDT desk clients."""

from __future__ import annotations

import logging
from typing import Final

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.models import Settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("lead-bot")

VOLUME, NETWORK, CONTACT = range(3)

NETWORKS: Final = ["TRC20", "BEP20", "ERC20", "Other"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message
    await update.effective_message.reply_text(
        "Welcome to the USDT desk assistant.\n"
        "We help serious buyers/sellers with clear rates and networks.\n\n"
        "Approximate monthly USDT volume? (e.g. 5k, 50k, 200k+)"
    )
    return VOLUME


async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.message and update.message.text
    context.user_data["volume"] = update.message.text.strip()
    rows = [[InlineKeyboardButton(n, callback_data=f"net:{n}")] for n in NETWORKS]
    await update.message.reply_text("Preferred network?", reply_markup=InlineKeyboardMarkup(rows))
    return NETWORK


async def network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    assert query and query.data
    await query.answer()
    context.user_data["network"] = query.data.split(":", 1)[1]
    await query.edit_message_text("Share contact / Telegram username / preferred fiat rail (UPI, bank, etc.):")
    return CONTACT


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.message and update.message.text and update.effective_user
    context.user_data["contact"] = update.message.text.strip()
    settings = Settings()
    summary = (
        f"New USDT lead\n"
        f"user={update.effective_user.id} @{update.effective_user.username}\n"
        f"volume={context.user_data.get('volume')}\n"
        f"network={context.user_data.get('network')}\n"
        f"contact={context.user_data.get('contact')}"
    )
    await update.message.reply_text(
        "Thanks — desk team will review and reply if there's a fit.\n"
        "No guaranteed returns; this is a buy/sell desk flow only."
    )
    if settings.telegram_admin_chat_id:
        try:
            await context.bot.send_message(settings.telegram_admin_chat_id, summary)
        except Exception as exc:  # noqa: BLE001
            log.warning("admin notify failed: %s", exc)
    log.info(summary.replace("\n", " | "))
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.effective_message
    await update.effective_message.reply_text("Cancelled.")
    return ConversationHandler.END


def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VOLUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, volume)],
            NETWORK: [CallbackQueryHandler(network, pattern=r"^net:")],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    return app


def main() -> None:
    settings = Settings()
    if not settings.telegram_bot_token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env")
    app = build_app(settings.telegram_bot_token)
    app.run_polling()


if __name__ == "__main__":
    main()
