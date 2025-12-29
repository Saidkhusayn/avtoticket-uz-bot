from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.cache import get_locations
from app.core.i18n import get_lang, t
from app.handlers.select_date import show_dates

async def show_to_location(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    locations = get_locations().get("locations", {})

    keyboard = [
            [InlineKeyboardButton(
                text=loc["names"].get(lang, loc["names"].get("uz", list(loc["names"].values())[0])),
                callback_data=f"to_location:{code}")]
                for code, loc in locations.items()
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
    lang = get_lang(update, context)
    location_code = str(context.user_data["to_location"])  # type: ignore

    locations = get_locations().get("locations", {})
    location = locations.get(location_code)
    if not location:
        return

    # exclude the from_station
    from_station_code = context.user_data.get("from_station")  # type: ignore

    keyboard = [
        [InlineKeyboardButton(
            text=stn["names"].get(lang, stn["names"].get("uz", next(iter(stn["names"].values())))),
            callback_data=f"to_station:{code}"
        )]
        for code, stn in location.get("stations", {}).items()
        if stn.get("can_arrive") and code != from_station_code
    ]

    markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(lang, "select.destination.station"),
            reply_markup=markup
        )

async def handle_to_station(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    station_code = query.data.split(":", 1)[1]  # type: ignore
    context.user_data["to_station"] = station_code  # type: ignore

    await show_dates(update, context, edit=True)