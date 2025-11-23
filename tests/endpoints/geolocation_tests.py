from __future__ import annotations

from functools import partial

import pytest
from conftest import make_test

from perekrestok_api import abstraction

# Локальные константы
MOSCOW_CENTER = abstraction.Geoposition(latitude=55.7558, longitude=37.6176)
MOSCOW_DELIVERY_POINT = abstraction.Geoposition(
    latitude=55.7655519, longitude=37.5916321
)


# Независимые тесты — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda api: api.Geolocation.current, id="current"),
        pytest.param(
            lambda api: api.Geolocation.delivery_address, id="delivery_address"
        ),
        pytest.param(
            lambda api: partial(api.Geolocation.Selection.delivery_info, MOSCOW_CENTER),
            id="delivery_info",
        ),
        pytest.param(
            lambda api: partial(api.Geolocation.address_from_position, MOSCOW_CENTER),
            id="address_from_position",
        ),
        pytest.param(
            lambda api: partial(api.Geolocation.suggests, "москва"), id="suggests"
        ),
        pytest.param(
            lambda api: partial(api.Geolocation.search, "москва", limit=5), id="search"
        ),
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
            lambda api: partial(
                api.Geolocation.Selection.delivery_point, MOSCOW_DELIVERY_POINT
            ),
            id="select_delivery_point",
        ),
    ],
)
async def test_geolocation_matrix(api, schemashot, factory):
    await make_test(schemashot, factory(api))


# Зависимая цепочка (нужен shop_id) — фикстура function-scoped
@pytest.fixture()
async def shop_id(api, schemashot) -> int:
    resp = await make_test(schemashot, api.Geolocation.Shop.all)
    return resp.json()["content"]["items"][0]["id"]


async def test_shop_info(api, schemashot, shop_id):
    await make_test(schemashot, partial(api.Geolocation.Shop.info, shop_id))


async def test_select_shop(api, schemashot, shop_id):
    await make_test(schemashot, partial(api.Geolocation.Selection.shop_point, shop_id))
