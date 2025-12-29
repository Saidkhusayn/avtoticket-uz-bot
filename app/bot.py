import logging
from telegram.ext import ApplicationBuilder, CommandHandler, Application, CallbackQueryHandler

from app.core.config import BOT_TOKEN, API_LOCATIONS_URL
from app.core.i18n import load_translations
from services.avtoticket import fetch_locations, normalize_locations
from services.cache import set_locations
from app.handlers.start import show_languages, set_language
from app.handlers.select_from import handle_from_location, handle_from_station
from app.handlers.select_to import handle_to_location, handle_to_station
from app.handlers.select_date import handle_date_page, handle_dates

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

    logger.info("Bot started")
    app.run_polling()