from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.cache import get_locations


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # type: ignore

    locations = get_locations().get("locations", {})
    keyboard = [
            [loc["names"]["en"]] for loc in locations.values()
        ]
    print(keyboard)
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    if update.effective_message:
        await update.effective_message.reply_text( 
            "Select departure date:",
            reply_markup=markup
        )
