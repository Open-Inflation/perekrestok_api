from __future__ import annotations

import pytest
from functools import partial
from perekrestok_api import abstraction
from conftest import make_test

# Локальные константы
MOSCOW_CENTER = abstraction.Geoposition(latitude=55.7558, longitude=37.6176)
MOSCOW_DELIVERY_POINT = abstraction.Geoposition(latitude=55.7655519, longitude=37.5916321)

# Независимые тесты — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda api: api.Geolocation.current, id="current"),
        pytest.param(lambda api: api.Geolocation.delivery_address, id="delivery_address"),
        pytest.param(lambda api: partial(api.Geolocation.Selection.delivery_info, MOSCOW_CENTER), id="delivery_info"),
        pytest.param(lambda api: partial(api.Geolocation.address_from_position, MOSCOW_CENTER), id="address_from_position"),
        pytest.param(lambda api: partial(api.Geolocation.suggests, "москва"), id="suggests"),
        pytest.param(lambda api: partial(api.Geolocation.search, "москва", limit=5), id="search"),
        pytest.param(lambda api: api.Geolocation.Shop.all, id="shop_all"),
        pytest.param(lambda api: api.Geolocation.Shop.features, id="shop_features"),
        pytest.param(
            lambda api: partial(
                api.Geolocation.Shop.on_map,
                position=MOSCOW_CENTER,
                limit=3,
                sort=abstraction.GeolocationPointSort.Distance.ASC,
            ),
            id="shops_on_map",
        ),
        pytest.param(
            lambda api: partial(api.Geolocation.Selection.delivery_point, MOSCOW_DELIVERY_POINT),
            id="select_delivery_point",
        ),
    ],
)
def test_geolocation_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Зависимая цепочка (нужен shop_id) — фикстура function-scoped
@pytest.fixture()
def shop_id(api, schemashot) -> int:
    resp = make_test(schemashot, api.Geolocation.Shop.all)
    return resp.json()["content"]["items"][0]["id"]


def test_shop_info(api, schemashot, shop_id):
    make_test(schemashot, partial(api.Geolocation.Shop.info, shop_id))


def test_select_shop(api, schemashot, shop_id):
    make_test(schemashot, partial(api.Geolocation.Selection.shop_point, shop_id))
