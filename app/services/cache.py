from __future__ import annotations
from typing import Any

_cache: dict[str, Any] = {}


def get_full_cache() -> dict[str, Any]:
    return _cache


def set_cache(key: str, value: Any) -> None:
    _cache[key] = value


def get_cache(key: str, default: Any = None) -> Any:
    return _cache.get(key, default)


def get_station_route(station_code: str) -> dict | None:
    routes = get_cache("station_routes", {})
    return routes.get(station_code)


def set_station_route(station_code: str, data: dict) -> None:
    routes = get_cache("station_routes", {})
    routes[station_code] = data
    set_cache("station_routes", routes)
