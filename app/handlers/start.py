from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.cache import get_locations


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Welcome! Use /select_from to choose your departure location."
        )