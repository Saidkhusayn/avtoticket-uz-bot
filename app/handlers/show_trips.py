from telegram import Update
from telegram.ext import ContextTypes
from app.core.i18n import get_lang, t
from app.services.avtoticket import get_trips

async def show_trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_station = context.user_data.get("from_station")  # type: ignore
    to_station = context.user_data.get("to_station")  # type: ignore
    date = context.user_data.get("selected_date")  # type: ignore

    trips = await get_trips(from_station, to_station, date) # type: ignore
    await update.effective_message.reply_text("Showing available bus trips...")  # type: ignore
