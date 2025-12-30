# from urllib import response
import json
# from telegram.ext import ContextTypes
import httpx
from app.core.config import API_LOCATIONS_URL, API_TRIPS_URL
from app.services.cache import get_station_routes, set_station_routes


async def fetch_locations() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(API_LOCATIONS_URL) # type: ignore
        response.raise_for_status()
        return response.json()

async def fetch_station_routes(station_code: str | int) -> dict:
    url = f"{API_LOCATIONS_URL}/{station_code}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_trips(from_station: str, to_station: str, date: str, days: int = 3) -> dict:
    async with httpx.AsyncClient() as client:
        payload = {
            "from": from_station,
            "to": to_station,
            "date": date,
            "days": days
        }
        response = await client.post(API_TRIPS_URL, json=payload) # type: ignore
        response.raise_for_status()
        with open("app/data/trips_response.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
        return response.json()

async def ensure_station_routes(station_code: str) -> dict:
    """
    Always returns the `data` dict for this station:
    {
      "from": {...},
      "to": {...},
      "locations": [],
      "stations": [],
      "apis": [...]
    }
    """
    cached = get_station_routes(station_code)
    if cached is not None:
        return cached 

    raw = await fetch_station_routes(station_code)

    if not raw.get("success"):
        raise ValueError(f"Invalid station routes response for {station_code}")

    data = raw["data"]

    set_station_routes(station_code, data)  # cache data-only

    return data