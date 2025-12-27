from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.core.i18n import t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        user_lang = update.effective_user.language_code or "en"

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