import pytest
from app.services.avtoticket import normalize_locations

# Sample raw API response (simplified)
RAW_SAMPLE = {
    "success": True,
    "data": {
        "from": {
            "locations": [{"code": 1, "name_ru": "A", "name_uz": "A", "name_en": "A"}],
            "stations": [{"code": 11, "location_code": 1, "name_ru": "S", "name_uz": "S", "name_en": "S"}]
        }
    }
}

def test_normalize_locations_basic():
    normalized = normalize_locations(RAW_SAMPLE)
    assert 1 in normalized["locations"]
    assert "stations" in normalized["locations"][1]
    assert 11 in normalized["locations"][1]["stations"]

def test_normalize_invalid_response():
    invalid = {"success": False}
    import pytest
    with pytest.raises(ValueError):
        normalize_locations(invalid)
