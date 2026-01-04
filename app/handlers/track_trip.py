from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.services.avtoticket import fetch_bus_seats
from app.core.i18n import get_lang, t
from app.services.cache import get_cache

logger = logging.getLogger(__name__)


def compute_free_seats(bus_resp: dict) -> tuple[int, int]:
    """
    Returns (free_seats, total_seats)
    """
    data = bus_resp.get("data", {}) or {}

    all_seats = data.get("all_seats", []) or []
    seat_numbers = [
        s.get("seat_number")
        for s in all_seats
        if s.get("type") == 1 and s.get("seat_number") is not None
    ]
    total = len(seat_numbers)

    reserved = set(data.get("reserved_seats", []) or [])
    sold = set((data.get("trip_data", {}) or {}).get("sold_seats", []) or [])

    unavailable = reserved | sold
    free = max(0, total - len(unavailable))
    return free, total


def _job_name(chat_id: int) -> str:
    return f"track_trip:{chat_id}"


def _remove_existing_job(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> int:
    jq = context.application.job_queue
    if not jq:
        return 0
    jobs = jq.get_jobs_by_name(_job_name(chat_id))
    for job in jobs:
        job.schedule_removal()
    return len(jobs)


def _seats_left_from_selected_trip(trip: dict) -> int | None:
    """
    Your trips list has:
      seats (total) and sold_seats (already sold count)
    So seats_left = seats - sold_seats
    """
    seats_total = trip.get("seats")
    sold = trip.get("sold_seats")
    if seats_total is None or sold is None:
        return None
    try:
        return int(seats_total) - int(sold)
    except Exception:
        return None


async def start_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    CallbackQuery handler: pattern="^track_trip$"
    """
    query = update.callback_query
    if not query:
        return

    await query.answer()

    lang = get_lang(update, context)

    trip = context.user_data.get("selected_trip")  # type: ignore
    if not isinstance(trip, dict):
        await query.edit_message_text("No trip selected.")
        return

    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return

    # Don't allow tracking if seats already look empty from trips list
    seats_left_guess = _seats_left_from_selected_trip(trip)
    if seats_left_guess is not None and seats_left_guess <= 0:
        msg = t(lang, "track.no_seats")
        await query.edit_message_text(msg)
        return

    trip_id = trip.get("id")
    from_id = trip.get("from_id")
    to_id = trip.get("to_id")
    trip_api_id = trip.get("api_id")

    apis = get_cache("apis", [])
    api_obj = apis[trip_api_id]
    if api_obj and api_obj.get("id") == trip_api_id:
        api_url = api_obj.get("url")

    if trip_id is None or from_id is None or to_id is None or api_url is None:
        await query.edit_message_text("Trip missing required IDs (id/from_id/to_id/api_url).")
        return

    removed = _remove_existing_job(context, chat_id)

    # thresholds to notify once when free seats become <= threshold
    thresholds = [30, 20, 10, 5, 3, 2, 1]

    job_data: dict[str, Any] = {
        "chat_id": chat_id,
        "trip_id": trip_id,
        "from_id": from_id,
        "to_id": to_id,
        "api": api_url,
        "thresholds": thresholds,
        "already_notified": set(),
        "last_free": None,
        "lang": lang,  # store lang at start
    }

    interval_seconds = int(context.user_data.get("track_interval", 60))  # type: ignore

    jq = context.application.job_queue
    if not jq:
        await query.edit_message_text("JobQueue is not enabled.")
        return

    logger.info(
        "Starting tracking chat_id=%s trip_id=%s from_id=%s to_id=%s interval=%ss removed_jobs=%s",
        chat_id, trip_id, from_id, to_id, interval_seconds, removed
    )

    jq.run_repeating(
        callback=_poll_trip_seats,
        interval=interval_seconds,
        first=0,
        name=_job_name(chat_id),
        data=job_data,
    )

    selected_trip_text = context.user_data.get("selected_trip_text", "")  # type: ignore

    # Immediate user feedback
    start_msg = (
        f"✅ Tracking started for:\n\n"
        f"{selected_trip_text}\n"
        f"{'♻️ Replaced previous tracking.' if removed else ''}\n"
        f"⏰ Check every {interval_seconds}s.\n"
        f"Use /stop_tracking to stop."
    )
    await query.edit_message_text(start_msg, parse_mode=ParseMode.HTML)


async def stop_tracking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command handler: /stop_tracking
    """
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return

    removed = _remove_existing_job(context, chat_id)
    logger.info("Stop tracking chat_id=%s removed_jobs=%s", chat_id, removed)

    lang = get_lang(update, context)
    msg = t(lang, "track.stopped")
    if update.effective_message:
        await update.effective_message.reply_text(msg)


async def _poll_trip_seats(context: ContextTypes.DEFAULT_TYPE):
    """
    Job callback. Uses context.job.data
    """
    job = context.job
    if job is None:
        return

    data = job.data or {}
    chat_id = data.get("chat_id") # type: ignore
    trip_id = data.get("trip_id") # type: ignore
    from_id = data.get("from_id") # type: ignore
    to_id = data.get("to_id") # type: ignore
    api = str(data.get("api")) if data.get("api") else "" # type: ignore
    thresholds = data.get("thresholds", []) # type: ignore
    already_notified: set[int] = data.get("already_notified", set()) # type: ignore

    if not (chat_id and trip_id and from_id and to_id):
        logger.warning("Tracking job missing ids: %s", data)
        return

    try:
        bus_resp = await fetch_bus_seats(api, from_id, to_id, trip_id)

        if not bus_resp.get("success"):
            logger.warning("Bus seats API returned success=false chat_id=%s trip_id=%s", chat_id, trip_id)
            return

        free, total = compute_free_seats(bus_resp)
        last_free = data.get("last_free") # type: ignore
        data["last_free"] = free # type: ignore

        logger.info("Seat poll chat_id=%s trip_id=%s free=%s total=%s last=%s", chat_id, trip_id, free, total, last_free)

        # If first poll, send a "current status" message (helps user trust it works)
        if last_free is None:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📍 Tracking active\nFree seats: <b>{free}</b> / {total}",
                parse_mode=ParseMode.HTML,
            )

        # Notify when crossing thresholds
        for th in thresholds:
            if free <= th and th not in already_notified:
                already_notified.add(th)
                text = (
                    f"🔔 <b>Seats update</b>\n"
                    f"Free seats: <b>{free}</b> / {total}\n"
                    f"⚠️ Now ≤ <b>{th}</b> seats."
                )
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

        # Sold out => notify and stop
        if free <= 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Sold out (0 seats left). Stopping tracking.",
            )
            job.schedule_removal()

    except Exception as e:
        logger.exception("Error polling seats chat_id=%s trip_id=%s,: %s", chat_id, trip_id, e)