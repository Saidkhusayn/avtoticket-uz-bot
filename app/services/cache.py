from __future__ import annotations
from typing import Any

_cache: dict[str, Any] = {}


def get_full_cache() -> dict[str, Any]:
    return _cache


def set_cache(key: str, value: Any) -> None:
    _cache[key] = value


def get_cache(key: str, default: Any = None) -> Any:
    return _cache.get(key, default)


# Optional tiny convenience wrappers (still using generic cache underneath)

def get_station_route(station_code: str) -> dict | None:
    routes = get_cache("station_routes", {})
    return routes.get(station_code)


def set_station_route(station_code: str, data: dict) -> None:
    routes = get_cache("station_routes", {})
    routes[station_code] = data
    set_cache("station_routes", routes)


# def set_locations(data: dict):
#     cache["locations"] = data

# def get_locations() -> dict:
#     return cache.get("locations", {})

# def set_station_routes(station_code: str, data: dict):
#     station_routes = cache.setdefault("station_routes", {})
#     station_routes[station_code] = data

# def get_station_routes(station_code: str) -> dict | None:
#     return cache.get("station_routes", {}).get(station_code)

# def set_trips(data: dict):
#     trips_cache = cache.setdefault("trips", {})
#     trips_cache["trips"] = data

# def get_trips() -> dict | None:
#     return cache.get("trips", {}).get("trips")