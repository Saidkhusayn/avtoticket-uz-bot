from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.cache import get_cache
from app.core.i18n import get_lang, t
from app.handlers.select_date import show_dates

async def show_to_location(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    
    data = context.user_data["routes_from_station"]  # type: ignore
    to_locations = data.get("to", {}).get("locations", [])

    locations = get_cache("master_locations", {})

    # from_location_code = str(context.user_data["from_location"])  # type: ignore
    # # exclude from_location
    # to_locations = [loc for loc in to_locations if loc["code"] != from_location_code]

    keyboard = []
    for loc in to_locations:
        code = str(loc["code"])
        location_code = locations.get(code, {})
        if location_code:
            label = location_code["names"].get(lang, location_code["names"].get("uz"))
        else:
            label = loc.get(f"name_{lang}", loc.get("name_uz"))
        
        keyboard.append([InlineKeyboardButton(
            text=label,
            callback_data=f"to_location:{code}"
        )])

    markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(lang, "select.destination.location"),
            reply_markup=markup
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
    to_location_code = str(context.user_data["to_location"])  # type: ignore
    from_station_code = str(context.user_data["from_station"])  # type: ignore

    data = context.user_data.get("routes_from_station", {}) # type: ignore
    to_stations = data.get("to", {}).get("stations", [])

    master_locations = get_cache("master_locations", {})

    filtered = [
        stn for stn in to_stations
        if str(stn["location_code"]) == to_location_code
           and str(stn["code"]) != from_station_code  # don't arrive at the same station
    ]

    keyboard = []
    for stn in filtered:
        stn_code = str(stn["code"])
        loc_code = str(stn["location_code"])

        master_loc = master_locations.get(loc_code, {})
        master_station = master_loc["stations"].get(stn_code) if master_loc else None

        if master_station: 
            label = master_station["names"].get(lang, master_station["names"].get("uz"))
        else:
            label = stn.get(f"name_{lang}", stn.get("name_uz"))

    keyboard = [
        [InlineKeyboardButton(
            text=label,
            callback_data=f"to_station:{stn_code}"
        )]
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