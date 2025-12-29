from telegram import Update
from telegram.ext import ContextTypes
from services.cache import get_locations
from app.core.i18n import get_lang, t

async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    locations = get_locations().get("locations", {})

    from_location_code = str(context.user_data.get("from_location", "")) # type: ignore
    to_location_code = str(context.user_data.get("to_location", "")) # type: ignore
    from_station_code = str(context.user_data.get("from_station", "")) # type: ignore
    to_station_code = str(context.user_data.get("to_station", "")) # type: ignore
    travel_date = context.user_data.get("selected_date", "") # type: ignore

    from_location = locations.get(from_location_code, {})
    to_location = locations.get(to_location_code, {})

    from_station = from_location.get("stations", {}).get(from_station_code, {})
    to_station = to_location.get("stations", {}).get(to_station_code, {})

    summary_text = (
        f"{t(lang, 'select.departure.location')} "
        f"{from_location.get('names', {}).get(lang, from_location.get('names', {}).get('uz', ''))}\n"
        f"{t(lang, 'select.departure.station')} "
        f"{from_station.get('names', {}).get(lang, from_station.get('names', {}).get('uz', ''))}\n\n"
        f"{t(lang, 'select.destination.location')} "
        f"{to_location.get('names', {}).get(lang, to_location.get('names', {}).get('uz', ''))}\n"
        f"{t(lang, 'select.destination.station')} "
        f"{to_station.get('names', {}).get(lang, to_station.get('names', {}).get('uz', ''))}\n\n"
        f"{t(lang, 'select.travel.date')} {travel_date}"
    )

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(summary_text)
    else:
        await update.message.reply_text(summary_text) # type: ignore