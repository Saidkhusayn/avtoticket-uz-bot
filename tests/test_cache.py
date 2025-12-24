from app.services.cache import get_locations, set_locations

def test_cache_set_get():
    data = {"foo": "bar"}
    set_locations(data)
    assert get_locations() == data