from __future__ import annotations

from typing import Any

import pytest
from human_requests import autotest_depends_on, autotest_hook, autotest_params
from human_requests.autotest import AutotestCallContext, AutotestContext

from perekrestok_api import abstraction
from perekrestok_api.endpoints.geolocation import (
    ClassGeolocation,
    GeolocationSelection,
    ShopService,
)

MOSCOW_CENTER = abstraction.Geoposition(latitude=55.7558, longitude=37.6176)
MOSCOW_DELIVERY_POINT = abstraction.Geoposition(
    latitude=55.7655519,
    longitude=37.5916321,
)


def _shop_id_params(ctx: AutotestCallContext):
    return {"shop_id": ctx.state["autotest_shop_id"]}


@autotest_params(target=ClassGeolocation.address_from_position)
def _address_from_position_params(
    _ctx: AutotestCallContext,
):
    return {"position": MOSCOW_CENTER}


@autotest_params(target=ClassGeolocation.suggests)
def _suggests_params(_ctx: AutotestCallContext):
    return {"search": "москва"}


@autotest_params(target=ClassGeolocation.search)
def _search_params(_ctx: AutotestCallContext):
    return {"search": "москва", "limit": 5}


@autotest_params(target=ShopService.on_map)
def _shops_on_map_params(_ctx: AutotestCallContext):
    return {
        "position": MOSCOW_CENTER,
        "limit": 3,
        "sort": abstraction.GeolocationPointSort.Distance.ASC,
    }


@autotest_params(target=GeolocationSelection.delivery_point)
def _delivery_point_params(_ctx: AutotestCallContext):
    return {"position": MOSCOW_DELIVERY_POINT}


@autotest_params(target=GeolocationSelection.delivery_info)
def _delivery_info_params(_ctx: AutotestCallContext):
    return {"position": MOSCOW_CENTER}


@autotest_hook(target=ShopService.all)
def _capture_shop_id(_resp: Any, data: dict[str, Any], ctx: AutotestContext) -> None:
    try:
        shop_id = data["content"]["items"][0]["id"]
    except (KeyError, IndexError, TypeError):
        pytest.fail("Shop.all did not return shop id.")
    if not isinstance(shop_id, int):
        pytest.fail("Shop.all returned non-int shop id.")
    ctx.state["autotest_shop_id"] = shop_id


@autotest_depends_on(ShopService.all)
@autotest_params(target=ShopService.info)
@autotest_params(target=GeolocationSelection.shop_point)
def _shop_info_params(ctx: AutotestCallContext):
    return _shop_id_params(ctx)
