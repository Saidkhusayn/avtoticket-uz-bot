from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date, timedelta
from babel.dates import format_date
from app.core.i18n import get_lang, t
from app.handlers.show_summary import show_summary

def format_day(d: date, lang: str) -> str:
    locale = {
        "en": "en",
        "ru": "ru",
        "uz": "uz"
    }.get(lang, "uz")

    return format_date(d, format="d MMM", locale=locale)

async def show_dates(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    lang = get_lang(update, context)
    
    offset = context.user_data.get("date_offset", 0)  # type: ignore
    today = date.today()

    days = [
        today + timedelta(days=offset + i)
        for i in range(7)
        if offset + i <= 30
    ]

    keyboard = [
        [InlineKeyboardButton(
            text=format_day(d, lang),
            callback_data=f"date:{d.strftime('%Y-%m-%d')}"
        )] for d in days
    ]

    nav = []

    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data="date_page:prev"))
    if offset + 7 < 30:
        nav.append(InlineKeyboardButton("➡️", callback_data="date_page:next"))

    if nav:
        keyboard.append(nav)

    markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            t(lang, "select.travel.date"),
            reply_markup=markup
        )

async def handle_date_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # type: ignore

    action = query.data.split(":")[1] # type: ignore
    offset = context.user_data.get("date_offset", 0) # type: ignore

    if action == "next":
        context.user_data["date_offset"] = offset + 7 # type: ignore
    elif action == "prev":
        context.user_data["date_offset"] = max(0, offset - 7) # type: ignore

    await show_dates(update, context, edit=True)

async def handle_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # type: ignore

    date_str = query.data.split(":")[1] # type: ignore
    context.user_data["selected_date"] = date_str # type: ignore

    await show_summary(update, context, edit=True)