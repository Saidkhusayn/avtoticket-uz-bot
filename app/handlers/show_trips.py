from __future__ import annotations
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.core.i18n import get_lang, t
from app.services.avtoticket import get_trips_data
from app.services.cache import get_full_cache

PAGE_SIZE = 5


def _safe(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt_time(dt_str: str) -> str:
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
    except Exception:
        return dt_str


def _money_uzs(x) -> str:
    try:
        return f"{int(x):,}".replace(",", " ")
    except Exception:
        return "-"


def _pick_route_name(trip: dict, lang: str) -> str:
    return trip.get(f"route_name_{lang}") or trip.get("route_name") or ""


def _build_flat_trips_window(days: list[dict], selected_date: str) -> tuple[list[dict], list[str], int]:
    by_date: dict[str, list[dict]] = {}
    for day in days:
        d = str(day.get("name", ""))
        trips = day.get("trips", []) or []
        if d:
            by_date[d] = trips

    sel = str(selected_date)
    sel_count = len(by_date.get(sel, []))

    date_to_show = [sel]

    flat: list[dict] = []
    for d in date_to_show:
        for trip in by_date.get(d, []):
            trip_copy = dict(trip)
            trip_copy["_day"] = d
            flat.append(trip_copy)

    return flat, date_to_show, sel_count


async def render_trips(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    """
    Renders from cached trips in user_data. NO API calls here.
    """
    lang = get_lang(update, context)
    selected_date = str(context.user_data.get("selected_date"))  # type: ignore
    days = context.user_data.get("trips_days", [])  # type: ignore

    if not days or not selected_date:
        msg = t(lang, "trips.none_found")
        if edit and update.callback_query:
            await update.callback_query.edit_message_text(msg)
        elif update.effective_message:
            await update.effective_message.reply_text(msg)
        return

    flat_trips, date_used, sel_count = _build_flat_trips_window(days, selected_date)
    context.user_data["flat_trips"] = flat_trips  # type: ignore
    with open("app/data/flat_trips.json", "w", encoding="utf-8") as f:
        import json
        json.dump(flat_trips, f, indent=4, ensure_ascii=False)

    total = len(flat_trips)
    if total == 0:
        msg = t(lang, "trips.none_found") if "trips.none_found" else "No trips found."
        if edit and update.callback_query:
            await update.callback_query.edit_message_text(msg)
        elif update.effective_message:
            await update.effective_message.reply_text(msg)
        return

    offset = int(context.user_data.get("trips_offset", 0))  # type: ignore
    offset = max(0, min(offset, max(0, total - 1)))
    context.user_data["trips_offset"] = offset  # type: ignore

    page = flat_trips[offset: offset + PAGE_SIZE]

    lines: list[str] = []
    lines.append(f"<b>{_safe(t(lang, 'trips.available'))}</b>")

    lines.append("")
    lines.append("<b>📅 Day:</b> " + " | ".join(
        [f"<u>{_safe(d)}</u>" if d == selected_date else _safe(d) for d in date_used]
    ))
    lines.append("")

    buttons: list[list[InlineKeyboardButton]] = []

    for i, trip in enumerate(page, start=offset + 1):
        # d = trip.get("_day", selected_date)
        dep = _fmt_time(trip.get("departure_at", ""))
        arr = _fmt_time(trip.get("arrive_at", ""))
        route = _safe(_pick_route_name(trip, lang))
        bus = _safe(trip.get("bus_model_name") or "-")
        price = _money_uzs(trip.get("price"))

        seats_total = trip.get("seats")
        sold = trip.get("sold_seats") or 0
        seats_left = None
        try:
            if seats_total is not None:
                seats_left = int(seats_total) - int(sold)
        except Exception:
            seats_left = None

        line1 = f"<b>{i})</b> <b>{_safe(dep)} → {_safe(arr)}</b>  |  <b>{_safe(price)}</b> so'm"
        if seats_left is not None:
            line1 += f"  |  🎟 {seats_left}"

        lines.append(line1)
        lines.append(f"  📍 {_safe(route)}")
        lines.append(f"   🚌 {bus}")
        lines.append("")

        buttons.append([InlineKeyboardButton(f"✅ {i}", callback_data=f"trip:{i}")])

    nav_row: list[InlineKeyboardButton] = []
    if offset > 0:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data="trips_page:prev"))
    if offset + PAGE_SIZE < total:
        nav_row.append(InlineKeyboardButton("➡️", callback_data="trips_page:next"))
    if nav_row:
        buttons.append(nav_row)

    lines.append(f"<i>Showing {offset + 1}-{min(offset + PAGE_SIZE, total)} of {total}</i>")

    text = "\n".join(lines)
    markup = InlineKeyboardMarkup(buttons)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
    else:
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)  # type: ignore


async def show_trips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetches trips ONCE per (from_station, to_station, selected_date),
    stores in user_data, then renders.
    """
    from_station = str(context.user_data.get("from_station"))  # type: ignore
    to_station = str(context.user_data.get("to_station"))      # type: ignore
    selected_date = str(context.user_data.get("selected_date"))  # type: ignore

    query_key = f"{from_station}:{to_station}:{selected_date}"
    last_key = context.user_data.get("trips_query_key")  # type: ignore

    # Fetch only if not cached for this query
    if last_key != query_key or "trips_days" not in context.user_data: # type: ignore
        trips_resp = await get_trips_data(from_station, to_station, selected_date)
        context.user_data["trips_days"] = trips_resp.get("data", [])  # type: ignore
        context.user_data["trips_query_key"] = query_key  # type: ignore
        context.user_data["trips_offset"] = 0  # reset paging  # type: ignore

    await render_trips(update, context, edit=False)


async def handle_trips_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    action = query.data.split(":", 1)[1]  # type: ignore
    offset = int(context.user_data.get("trips_offset", 0))  # type: ignore
    flat_trips = context.user_data.get("flat_trips", [])  # type: ignore
    total = len(flat_trips)

    if action == "next":
        offset = min(max(0, total - 1), offset + PAGE_SIZE)
    else:
        offset = max(0, offset - PAGE_SIZE)

    context.user_data["trips_offset"] = offset  # type: ignore
    await render_trips(update, context, edit=True)

async def handle_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    lang = get_lang(update, context)
    trip_index = int(query.data.split(":", 1)[1]) - 1  # type: ignore
    flat_trips = context.user_data.get("flat_trips", [])  # type: ignore
    trip = flat_trips[trip_index]
    selected_date = context.user_data.get("selected_date", "")  # type: ignore

    context.user_data["selected_trip"] = trip # type: ignore

    d = trip.get("_day", selected_date)
    dep = _fmt_time(trip.get("departure_at", ""))
    arr = _fmt_time(trip.get("arrive_at", ""))
    route = _safe(_pick_route_name(trip, lang))
    bus = _safe(trip.get("bus_model_name") or "-")
    price = _money_uzs(trip.get("price"))

    lines: list[str] = []

    line1 = f"<b>{_safe(d)}</b>  |  <b>{_safe(dep)} → {_safe(arr)}</b>  |  <b>{_safe(price)}</b> so'm"

    lines.append(line1)
    lines.append(f"  📍 {_safe(route)}")
    lines.append(f"   🚌 {bus}")
    lines.append("")

    text = "\n".join(lines)

    context.user_data["selected_trip_text"] = text # type: ignore

    markup = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔔 Track seats", callback_data="track_trip")]
])

    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)