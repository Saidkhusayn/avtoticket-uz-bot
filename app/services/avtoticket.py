import httpx
from collections import defaultdict

async def fetch_locations(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def normalize_locations(raw: dict) -> dict:
    """
    Takes raw /api-locations response (dict)
    Returns normalized, bot-friendly structure
    """

    # 1. Validate minimal structure (fail early)
    if not raw or not raw.get("success"):
        raise ValueError("Invalid api-locations response")

    data = raw["data"]

    normalized = {
        "locations": {}
    }

    # 2. Normalize 'from' locations
    from_locations = data.get("from", {}).get("locations", [])
    from_stations = data.get("from", {}).get("stations", [])

    for loc in from_locations:
        code = loc["code"]

        if code not in normalized["locations"]:
            normalized["locations"][code] = {}

        normalized["locations"][code]["names"] = {
            "ru": loc["name_ru"],
            "uz": loc["name_uz"],
            "en": loc["name_en"]
        }
        
    # 3. Normalize 'from' stations under their respective locations
    for stn in from_stations:
        loc_code = stn["location_code"]
        stn_code = stn["code"]

        if "stations" not in normalized["locations"][loc_code]:
            normalized["locations"][loc_code]["stations"] = {}

        normalized["locations"][loc_code]["stations"][stn_code] = {
            "ru": stn["name_ru"],
            "uz": stn["name_uz"],
            "en": stn["name_en"]
        }

    return normalized

def run_test():
    import asyncio
    import json

    async def test():
        data = await fetch_locations("https://wapi.avtoticket.uz/api/api-locations")
        normalized = normalize_locations(data)
        json_data = json.dumps(normalized, ensure_ascii=False, indent=2)
        with open("app/data/normalized_data.json", "w", encoding="utf-8") as f:
            f.write(json_data)

    asyncio.run(test())

if __name__ == "__main__":
    run_test()
    print("Done.")
    