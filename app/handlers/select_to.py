from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.cache import get_locations
from app.core.i18n import get_lang, t

async def show_to_location(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    locations = get_locations().get("locations", {})

    keyboard = [
            [InlineKeyboardButton(
                text=loc["names"].get(lang, loc["names"].get("uz", list(loc["names"].values())[0])),
                callback_data=f"to_location:{code}")]
                for code, loc in locations.items() # exclude the deparutre location
                if loc.get("can_arrive")
        ]

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(lang, "select.destination.location"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_to_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    location_code = query.data.split(":", 1)[1]  # type: ignore
    context.user_data["to_location"] = location_code  # type: ignore

    await show_to_station(update, context, edit=True)

async def show_to_station(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    pass
    # Further processing can be done here, such as prompting for destination station selection