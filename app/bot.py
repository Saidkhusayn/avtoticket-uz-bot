import logging
from telegram.ext import ApplicationBuilder, CommandHandler, Application, CallbackQueryHandler

from app.core.config import BOT_TOKEN, API_LOCATIONS_URL
from app.core.i18n import load_translations
from services.avtoticket import fetch_locations, normalize_locations
from services.cache import set_locations
from app.handlers.start import show_languages, set_language
from app.handlers.select_from import (
    show_from_location,
    handle_from_location,
    show_from_station
)

# LOGGING (module-level is fine)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def on_startup(app: Application) -> None:
    raw_data = await fetch_locations(API_LOCATIONS_URL) # type: ignore
    normalized = normalize_locations(raw_data)
    set_locations(normalized)
    load_translations()
    print("Locations data cached and translations loaded.")

def run_bot() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build() # type: ignore

    app.add_handler(CommandHandler("start", show_languages))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang:"))

    app.add_handler(CallbackQueryHandler(handle_from_location, pattern="^from_location:"))
    app.add_handler(CallbackQueryHandler(show_from_station, pattern="^from_station:"))

    logger.info("Bot started")
    app.run_polling()