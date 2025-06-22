import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT
from conftest import is_not_error


def test_current_geolocation(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.current()
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "current_geolocation")

def test_delivery_address(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.delivery_address()
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "delivery_address")

def test_delivery_info(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.Selection.delivery_info(ABSTRACT.Geoposition(latitude=55.75582, longitude=37.61729))
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "delivery_info")

def test_address_from_position(api: PerekrestokAPI, schemashot: SchemaShot):
    position = ABSTRACT.Geoposition(latitude=55.7558, longitude=37.6176)  # Moscow coordinates
    resp = api.Geolocation.address_from_position(position)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "address_from_position")

def test_geocoder_suggests(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.suggests("москва")
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "geocoder_suggests")

def test_search_geolocation(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.search("москва", limit=5)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "search_geolocation")

async def test_get_all_shops_and_shop_info(api: PerekrestokAPI, schemashot: SchemaShot):
    # First get list of shops to get ID
    shops_resp = api.Geolocation.Shop.all()
    is_not_error(shops_resp)
    shops_resp_data = shops_resp.json()
    schemashot.assert_match(shops_resp_data, "all_shops")
    shop_id = shops_resp_data["content"]["items"][0]["id"]

    resp = api.Geolocation.Shop.info(shop_id)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "shop_info")

    resp = api.Geolocation.Selection.shop_point(shop_id)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "select_shop")


def test_shops_on_map(api: PerekrestokAPI, schemashot: SchemaShot):
    # Moscow coordinates (latitude, longitude)
    position = ABSTRACT.Geoposition(55.7558, 37.6176)
    resp = api.Geolocation.Shop.on_map(
        position=position,
        limit=3,
        sort=ABSTRACT.GeolocationPointSort.Distance.ASC
    )
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "shops_on_map")


def test_shop_features(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Geolocation.Shop.features()
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "shop_features")


def test_select_delivery_point(api: PerekrestokAPI, schemashot: SchemaShot):
    # Moscow coordinates
    position = ABSTRACT.Geoposition(55.7655519, 37.5916321)
    resp = api.Geolocation.Selection.delivery_point(position)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "select_delivery_point")
