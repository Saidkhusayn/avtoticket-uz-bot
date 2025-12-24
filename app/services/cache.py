cache = {}

def set_locations(data: dict):
    cache["locations"] = data

def get_locations() -> dict:
    return cache.get("locations", {})