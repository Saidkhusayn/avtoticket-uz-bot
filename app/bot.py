import logging
from telegram.ext import ApplicationBuilder, CommandHandler, Application

from app.core.config import BOT_TOKEN, API_LOCATIONS_URL
from services.avtoticket import fetch_locations, normalize_locations
from services.cache import set_locations
from app.handlers.start import start

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
    print("Locations data fetched and cached.")

def run_bot() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build() # type: ignore

    app.add_handler(CommandHandler("start", start))

    logger.info("Bot started")
    app.run_polling()