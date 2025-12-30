cache = {}

def set_locations(data: dict):
    cache["locations"] = data

def get_locations() -> dict:
    return cache.get("locations", {})

def set_station_routes(station_code: str, data: dict):
    station_routes = cache.setdefault("station_routes", {})
    station_routes[station_code] = data

def get_station_routes(station_code: str) -> dict | None:
    return cache.get("station_routes", {}).get(station_code)