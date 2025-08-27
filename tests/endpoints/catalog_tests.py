from __future__ import annotations

import pytest
from functools import partial
from perekrestok_api import abstraction
from conftest import make_test

# Локальные константы
DEFAULT_LIMIT = 5

# Независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda api: api.Catalog.tree, id="tree"),
    ],
)
def test_catalog_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Зависимые фикстуры — function-scoped

@pytest.fixture()
def first_category_id(api, schemashot) -> int:
    """ID первой категории из корневого дерева."""
    resp = make_test(schemashot, api.Catalog.tree)
    data = resp.json()
    return data["content"]["items"][0]["category"]["id"]

@pytest.fixture()
def first_subcategory_id(api, schemashot, first_category_id) -> int:
    """ID первой подкатегории первой категории."""
    resp = make_test(schemashot, api.Catalog.tree)
    data = resp.json()
    return data["content"]["items"][0]["children"][0]["category"]["id"]

def test_category_info(api, schemashot, first_category_id):
    make_test(schemashot, partial(api.Catalog.category_info, first_category_id))

def test_category_reviews(api, schemashot, first_category_id):
    make_test(schemashot, partial(api.Catalog.category_reviews, first_category_id))

def test_form_for_category(api, schemashot, first_category_id):
    flt = abstraction.CatalogFeedFilter()
    flt.CATEGORY_ID = first_category_id
    make_test(schemashot, partial(api.Catalog.form, filter=flt))

def test_grouped_feed_for_category(api, schemashot, first_category_id):
    flt = abstraction.CatalogFeedFilter()
    flt.CATEGORY_ID = first_category_id
    make_test(
        schemashot,
        partial(
            api.Catalog.grouped_feed,
            filter=flt,
            sort=abstraction.CatalogFeedSort.Price.ASC,
            limit=DEFAULT_LIMIT,
        ),
    )

def test_feed_for_category(api, schemashot, first_category_id):
    flt = abstraction.CatalogFeedFilter()
    flt.CATEGORY_ID = first_category_id
    make_test(
        schemashot,
        partial(
            api.Catalog.feed,
            filter=flt,
            sort=abstraction.CatalogFeedSort.Price.ASC,
            limit=DEFAULT_LIMIT,
        ),
    )

@pytest.fixture()
def product_ids(api, schemashot, first_category_id):
    """Берём первый товар из фида категории."""
    flt = abstraction.CatalogFeedFilter()
    flt.CATEGORY_ID = first_category_id
    resp = make_test(
        schemashot,
        partial(
            api.Catalog.feed,
            filter=flt,
            sort=abstraction.CatalogFeedSort.Price.ASC,
            limit=1,
        ),
        name="for_first_product",
    )
    item = resp.json()["content"]["items"][0]
    return {
        "product_id": item["id"],
        "product_plu": item["masterData"]["plu"],
    }

def test_product_info(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.info, product_ids["product_plu"]))

def test_product_similar(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.similar, product_ids["product_id"]))

def test_product_categories(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.categories, product_ids["product_plu"]))

def test_product_available_count(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.available_count, product_ids["product_plu"]))

def test_product_reviews_count(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.reviews_count, product_ids["product_plu"]))

def test_product_reviews(api, schemashot, product_ids):
    make_test(schemashot, partial(api.Catalog.Product.reviews, product_ids["product_plu"]))
