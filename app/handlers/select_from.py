from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.cache import get_locations
from app.core.i18n import get_lang, t


async def show_from_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = get_locations().get("locations", {})
    lang = get_lang(update, context)

    keyboard = [
            [InlineKeyboardButton(
                text=loc["names"][lang],
                callback_data=f"from_location:{code}")]
                for code, loc in locations.items()
        ]

    if update.effective_message:
        await update.effective_message.reply_text( 
            t(lang, "select.departure.location"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_from_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    lang = get_lang(update, context)

    location_code = query.data.split(":", 1)[1] # type: ignore
    context.user_data["from_location"] = location_code # type: ignore

    await query.edit_message_text(
        t(lang, "select.departure.station")
    )

    await show_from_station(update, context)

async def show_from_station(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)

    location_code = str(context.user_data["from_location"])  # type: ignore

    locations = get_locations().get("locations", {})
    location = locations.get(location_code)

    if not location:
    # optional: handle error nicely
        if update.effective_message:
            await update.effective_message.reply_text("Location not found 🤔")
        return

    stations = location.get("stations", {})

    keyboard = [
            [InlineKeyboardButton(
                text=stn.get(lang, stn.get("uz", list(stn.values())[0])),
                callback_data=f"from_station:{code}")]
                for code, stn in stations.items()
        ]

    if update.effective_message:
        await update.effective_message.reply_text( 
            t(lang, "select.departure.station"),
            reply_markup=InlineKeyboardMarkup(keyboard)
    )
        
    # check for can_departure flag in station data if needed