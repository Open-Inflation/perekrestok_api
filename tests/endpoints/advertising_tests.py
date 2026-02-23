from __future__ import annotations

from typing import Any

import pytest
from human_requests import autotest_depends_on, autotest_hook, autotest_params
from human_requests.autotest import AutotestCallContext, AutotestContext

from perekrestok_api import abstraction
from perekrestok_api.endpoints.advertising import ClassAdvertising

MOSCOW_CITY_ID = 81
DEFAULT_LIMIT = 5


@autotest_params(target=ClassAdvertising.banner)
def _banner_params(_ctx: AutotestCallContext):
    return {"places": [abstraction.BannerPlace.MAIN_BANNERS]}


@autotest_params(target=ClassAdvertising.main_slider)
def _main_slider_params(_ctx: AutotestCallContext):
    return {"page": 1, "limit": DEFAULT_LIMIT}


@autotest_params(target=ClassAdvertising.booklet)
def _booklet_params(_ctx: AutotestCallContext):
    return {"city": MOSCOW_CITY_ID}


@autotest_hook(target=ClassAdvertising.booklet)
def _capture_booklet_id(_resp: Any, data: dict[str, Any], ctx: AutotestContext) -> None:
    try:
        booklet_id = data["content"]["items"][0]["id"]
    except (KeyError, IndexError, TypeError):
        pytest.fail("Advertising.booklet did not return booklet id.")
    if not isinstance(booklet_id, int):
        pytest.fail("Advertising.booklet returned non-int booklet id.")
    ctx.state["autotest_booklet_id"] = booklet_id


@autotest_depends_on(ClassAdvertising.booklet)
@autotest_params(target=ClassAdvertising.view_booklet)
def _view_booklet_params(ctx: AutotestCallContext):
    return {"booklet_id": ctx.state["autotest_booklet_id"]}
