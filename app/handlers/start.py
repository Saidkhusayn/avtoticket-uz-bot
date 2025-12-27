from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.core.i18n import t
from app.handlers.select_from import show_from_location


async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        user_lang = update.effective_user.language_code or "uz"

    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang:en")],
        [InlineKeyboardButton("Русский", callback_data="lang:ru")],
        [InlineKeyboardButton("O‘zbek", callback_data="lang:uz")]
    ]
    if update.message:
        await update.message.reply_text(
            t(user_lang, "start.choose_language"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    lang = query.data.split(":", 1)[1] # type: ignore
    context.user_data["lang"] = lang # type: ignore

    await query.edit_message_text(
        t(lang, "start.welcome")
    )
    await show_from_location(update, context)