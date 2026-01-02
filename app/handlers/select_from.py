from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.cache import get_cache
from app.core.i18n import get_lang, t
from app.handlers.select_to import show_to_location
from app.services.avtoticket import ensure_station_routes


async def show_from_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = get_cache("master_locations", {})
    lang = get_lang(update, context)

    keyboard = [
            [InlineKeyboardButton(
                text=loc["names"].get(lang, loc["names"].get("uz", list(loc["names"].values())[0])),
                callback_data=f"from_location:{code}")]
                for code, loc in locations.items()
                if loc.get("can_depart")
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

    location_code = query.data.split(":", 1)[1] # type: ignore
    context.user_data["from_location"] = location_code # type: ignore

    await show_from_station(update, context, edit=True)

async def show_from_station(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    location_code = str(context.user_data["from_location"])  # type: ignore

    locations = get_cache("master_locations", {})
    location = locations.get(location_code)
    if not location:
        return

    keyboard = [
        [InlineKeyboardButton(
            text=stn["names"].get(lang, stn["names"].get("uz", next(iter(stn["names"].values())))),
            callback_data=f"from_station:{code}"
        )]
        for code, stn in location.get("stations", {}).items()
        if stn.get("can_depart")
    ]

    markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(lang, "select.departure.station"),
            reply_markup=markup
        )

async def handle_from_station(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    station_code = query.data.split(":", 1)[1]  # type: ignore
    context.user_data["from_station"] = station_code  # type: ignore

    routes_data = await ensure_station_routes(station_code)
    context.user_data["routes_from_station"] = routes_data # type: ignore

    await show_to_location(update, context, edit=True)