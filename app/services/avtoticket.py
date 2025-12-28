import httpx

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

    # Validate minimal structure (fail early)
    if not raw or not raw.get("success"):
        raise ValueError("Invalid api-locations response")

    data = raw["data"]

    # Location-level allow lists
    loc_from_codes = {loc["code"] for loc in data["from"]["locations"]}
    loc_to_codes = {loc["code"] for loc in data["to"]["locations"]}

    # Station-level allow lists
    stn_from_codes = {stn["code"] for stn in data["from"]["stations"]}
    stn_to_codes = {stn["code"] for stn in data["to"]["stations"]}

    normalized = {"locations": {}}

    # 1) Base locations (all known locations)
    for loc in data["locations"]:
        code = loc["code"]
        code_str = str(code)

        normalized["locations"][code_str] = {
            "names": {
                "ru": loc["name_ru"],
                "uz": loc["name_uz"],
                "en": loc["name_en"],
            }, 
            "stations": {},
            "can_depart": code in loc_from_codes,
            "can_arrive": code in loc_to_codes,
        }

    # 2) Stations (nested under locations)
    for stn in data["stations"]:
        loc_code_str = str(stn["location_code"])
        if loc_code_str not in normalized["locations"]:
            continue

        normalized["locations"][loc_code_str]["stations"][str(stn["code"])] = {
            "names": {
                "ru": stn["name_ru"],
                "uz": stn["name_uz"],
                "en": stn["name_en"],
            },
            "can_depart": stn["code"] in stn_from_codes,
            "can_arrive": stn["code"] in stn_to_codes,      
        }
    
    return normalized