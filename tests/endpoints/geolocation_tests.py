# geolocation_tests.py
from __future__ import annotations

import pytest
from functools import partial
from perekrestok_api import abstraction
from conftest import make_test

# Локальные константы для этого файла
MOSCOW_CENTER = abstraction.Geoposition(latitude=55.7558, longitude=37.6176)
MOSCOW_DELIVERY_POINT = abstraction.Geoposition(latitude=55.7655519, longitude=37.5916321)

# Все независимые тесты — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        # Базовые
        lambda api: api.Geolocation.current,
        lambda api: api.Geolocation.delivery_address,
        lambda api: partial(api.Geolocation.Selection.delivery_info, MOSCOW_CENTER),
        lambda api: partial(api.Geolocation.address_from_position, MOSCOW_CENTER),
        lambda api: partial(api.Geolocation.suggests, "москва"),
        lambda api: partial(api.Geolocation.search, "москва", limit=5),

        # Магазины/карта/фичи — тоже независимы
        lambda api: api.Geolocation.Shop.all,
        lambda api: api.Geolocation.Shop.features,
        lambda api: partial(
            api.Geolocation.Shop.on_map,
            position=MOSCOW_CENTER,
            limit=3,
            sort=abstraction.GeolocationPointSort.Distance.ASC,
        ),
        lambda api: partial(
            api.Geolocation.Selection.delivery_point,
            MOSCOW_DELIVERY_POINT,
        ),
    ],
    ids=[
        "current",
        "delivery_address",
        "delivery_info",
        "address_from_position",
        "suggests",
        "search",
        "shop_all",
        "shop_features",
        "shops_on_map",
        "select_delivery_point",
    ],
)
def test_geolocation_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Зависимая цепочка: нужен shop_id из списка магазинов
@pytest.fixture(scope="module")
def shop_id(api, schemashot) -> int:
    resp = make_test(schemashot, api.Geolocation.Shop.all)
    return resp.json()["content"]["items"][0]["id"]


def test_shop_info(api, schemashot, shop_id):
    make_test(schemashot, partial(api.Geolocation.Shop.info, shop_id))


def test_select_shop(api, schemashot, shop_id):
    make_test(schemashot, partial(api.Geolocation.Selection.shop_point, shop_id))
