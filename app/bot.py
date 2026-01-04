import logging
from telegram.ext import ApplicationBuilder, CommandHandler, Application, CallbackQueryHandler

from app.core.config import BOT_TOKEN
from app.core.i18n import load_translations
from app.services.avtoticket import fetch_locations
from app.domain.locations import normalize_locations
from app.services.cache import set_cache
from app.handlers.start import show_languages, set_language
from app.handlers.select_from import handle_from_location, handle_from_station
from app.handlers.select_to import handle_to_location, handle_to_station
from app.handlers.select_date import handle_date_page, handle_dates
from app.handlers.show_trips import handle_trips_page, handle_trip
from app.handlers.track_trip import start_tracking, stop_tracking

# LOGGING (module-level is fine)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def on_startup(app: Application) -> None:
    raw_data = await fetch_locations()
    normalized = normalize_locations(raw_data)
    set_cache("master_locations", normalized["locations"])
    set_cache("apis", raw_data["data"]["apis"]) # cache api urls
    load_translations()
    print("Locations data cached and translations loaded.")

def run_bot() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build() # type: ignore
    
    # SETUP HANDLERS
    app.add_handler(CommandHandler("start", show_languages))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang:"))
    
    # SELECT FROM HANDLERS
    app.add_handler(CallbackQueryHandler(handle_from_location, pattern="^from_location:"))
    app.add_handler(CallbackQueryHandler(handle_from_station, pattern="^from_station:"))
    
    # SELECT TO HANDLERS   
    app.add_handler(CallbackQueryHandler(handle_to_location, pattern="^to_location:"))
    app.add_handler(CallbackQueryHandler(handle_to_station, pattern="^to_station:"))
    
    # SELECT DATE HANDLERS
    app.add_handler(CallbackQueryHandler(handle_date_page, pattern="^date_page:"))
    app.add_handler(CallbackQueryHandler(handle_dates, pattern="^date:"))

    # SHOW TRIPS HANDLERS
    app.add_handler(CallbackQueryHandler(handle_trips_page, pattern="^trips_page:"))
    app.add_handler(CallbackQueryHandler(handle_trip, pattern="^trip:"))

    # TRACK TRIP HANDLERS
    app.add_handler(CallbackQueryHandler(start_tracking, pattern="^track_trip$"))
    app.add_handler(CommandHandler("stop_tracking", stop_tracking))
    # app.add_handler(CallbackQueryHandler(stop_track_btn, pattern="^stop_track_btn$"))

    logger.info("Bot started")
    app.run_polling()