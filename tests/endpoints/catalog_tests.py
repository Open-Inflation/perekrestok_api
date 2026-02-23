from __future__ import annotations

from typing import Any

import pytest
from human_requests import autotest_depends_on, autotest_hook, autotest_params
from human_requests.autotest import AutotestCallContext, AutotestContext

from perekrestok_api import abstraction
from perekrestok_api.endpoints.catalog import ClassCatalog, ProductService

DEFAULT_LIMIT = 48


def _category_filter(category_id: int) -> abstraction.CatalogFeedFilter:
    flt = abstraction.CatalogFeedFilter()
    flt.CATEGORY_ID = category_id
    return flt


@autotest_hook(target=ClassCatalog.tree)
def _capture_category_ids(_resp: Any, data: dict[str, Any], ctx: AutotestContext) -> None:
    try:
        first_item = data["content"]["items"][0]
        category_id = first_item["category"]["id"]
    except (KeyError, IndexError, TypeError):
        pytest.fail("Catalog.tree did not return category id.")
    if not isinstance(category_id, int):
        pytest.fail("Catalog.tree returned non-int category id.")

    ctx.state["autotest_first_category_id"] = category_id

    try:
        subcategory_id = first_item["children"][0]["category"]["id"]
    except (KeyError, IndexError, TypeError):
        return
    if isinstance(subcategory_id, int):
        ctx.state["autotest_first_subcategory_id"] = subcategory_id


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.category_info)
@autotest_params(target=ClassCatalog.category_reviews)
@autotest_params(target=ClassCatalog.preview_feed)
def _category_id_params(ctx: AutotestCallContext):
    return {"category_id": ctx.state["autotest_first_category_id"]}


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.form)
def _form_params(ctx: AutotestCallContext):
    return {"filter": _category_filter(ctx.state["autotest_first_category_id"])}


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.feed)
def _feed_params(ctx: AutotestCallContext):
    return {
        "filter": _category_filter(ctx.state["autotest_first_category_id"]),
        "sort": abstraction.CatalogFeedSort.Price.ASC,
        "limit": DEFAULT_LIMIT,
    }


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.grouped_feed)
def _grouped_feed_params(ctx: AutotestCallContext):
    return {
        "filter": _category_filter(ctx.state["autotest_first_subcategory_id"]),
        "sort": abstraction.CatalogFeedSort.Price.ASC,
        "limit": DEFAULT_LIMIT,
    }


@autotest_params(target=ClassCatalog.search)
def _search_params(_ctx: AutotestCallContext):
    return {"query": "молоко"}


@autotest_hook(target=ClassCatalog.feed)
def _capture_product_ids(_resp: Any, data: dict[str, Any], ctx: AutotestContext) -> None:
    try:
        first_product = data["content"]["items"][0]
        product_id = first_product["id"]
        product_plu = first_product["masterData"]["plu"]
    except (KeyError, IndexError, TypeError):
        pytest.fail("Catalog.feed did not return product ids.")

    if isinstance(product_id, int):
        ctx.state["autotest_product_id"] = product_id
    if isinstance(product_plu, (int, str)):
        ctx.state["autotest_product_plu"] = product_plu


@autotest_depends_on(ClassCatalog.feed)
@autotest_params(target=ProductService.info)
@autotest_params(target=ProductService.categories)
@autotest_params(target=ProductService.available_count)
@autotest_params(target=ProductService.reviews_count)
@autotest_params(target=ProductService.reviews)
def _product_plu_params(ctx: AutotestCallContext):
    return {"product_plu": ctx.state["autotest_product_plu"]}


@autotest_depends_on(ClassCatalog.feed)
@autotest_params(target=ProductService.similar)
def _product_similar_params(ctx: AutotestCallContext):
    return {"product_id": ctx.state["autotest_product_id"]}
