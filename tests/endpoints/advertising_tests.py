# advertising_tests.py
from __future__ import annotations

import pytest
from functools import partial
from perekrestok_api import abstraction
from conftest import make_test

# Локальные константы
MOSCOW_CITY_ID = 81
DEFAULT_LIMIT = 5

# Все независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        # Баннеры на главной
        lambda api: partial(
            api.Advertising.banner,
            [abstraction.BannerPlace.MAIN_BANNERS],
        ),
        # Главный слайдер
        lambda api: partial(api.Advertising.main_slider, page=1, limit=DEFAULT_LIMIT),
        # Буклеты для города
        lambda api: partial(api.Advertising.booklet, city=MOSCOW_CITY_ID),
    ],
    ids=["banner", "main_slider", "booklet"],
)
def test_advertising_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Зависимый тест: просмотр конкретного буклета
@pytest.fixture(scope="module")
def booklet_id(api, schemashot) -> int:
    resp = make_test(schemashot, partial(api.Advertising.booklet, city=MOSCOW_CITY_ID))
    return resp.json()["content"]["items"][0]["id"]


def test_view_booklet(api, schemashot, booklet_id):
    make_test(schemashot, partial(api.Advertising.view_booklet, booklet_id))
