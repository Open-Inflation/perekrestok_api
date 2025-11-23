from __future__ import annotations

from functools import partial

import pytest
from conftest import make_test

from perekrestok_api import abstraction

# Локальные константы
MOSCOW_CITY_ID = 81
DEFAULT_LIMIT = 5


# Независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(
            lambda api: partial(
                api.Advertising.banner,
                [abstraction.BannerPlace.MAIN_BANNERS],
            ),
            id="banner",
        ),
        pytest.param(
            lambda api: partial(
                api.Advertising.main_slider, page=1, limit=DEFAULT_LIMIT
            ),
            id="main_slider",
        ),
        pytest.param(
            lambda api: partial(api.Advertising.booklet, city=MOSCOW_CITY_ID),
            id="booklet",
        ),
    ],
)
async def test_advertising_matrix(api, schemashot, factory):
    await make_test(schemashot, factory(api))


# Зависимая фикстура — function-scoped
@pytest.fixture()
async def booklet_id(api, schemashot) -> int:
    resp = await make_test(
        schemashot, partial(api.Advertising.booklet, city=MOSCOW_CITY_ID)
    )
    return resp.json()["content"]["items"][0]["id"]


async def test_view_booklet(api, schemashot, booklet_id):
    await make_test(schemashot, partial(api.Advertising.view_booklet, booklet_id))
