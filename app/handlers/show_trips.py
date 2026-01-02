from telegram import Update
from telegram.ext import ContextTypes
from app.core.i18n import get_lang, t
from app.services.avtoticket import get_trips_data
from app.services.cache import set_cache, get_cache, get_full_cache

async def show_trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_station = context.user_data.get("from_station")  # type: ignore
    to_station = context.user_data.get("to_station")  # type: ignore
    date = context.user_data.get("selected_date")  # type: ignore

    trips = await get_trips_data(from_station, to_station, date) # type: ignore
    
    set_cache("trips", trips["data"]) 

    # debug snapshot
    full_cache = get_full_cache()
    with open("app/data/cache.json", "w", encoding="utf-8") as f:
        import json
        json.dump(full_cache, f, indent=2, ensure_ascii=False)
    await update.effective_message.reply_text("Showing available bus trips...")  # type: ignore