# catalog_tests.py
from __future__ import annotations

import pytest
from functools import partial
from conftest import make_test

# Локальные константы
DEFAULT_LIMIT = 5

# Независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        lambda api: api.Catalog.main,
        lambda api: api.Catalog.category_tree,
        lambda api: partial(api.Catalog.search, "молоко", page=1, limit=DEFAULT_LIMIT),
    ],
    ids=["main", "category_tree", "search"],
)
def test_catalog_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Зависимые кейсы — через фикстуры
@pytest.fixture(scope="module")
def first_category_id(api, schemashot) -> int:
    resp = make_test(schemashot, api.Catalog.category_tree)
    return resp.json()["content"]["children"][0]["id"]


def test_category_list(api, schemashot, first_category_id):
    make_test(
        schemashot,
        partial(api.Catalog.category, first_category_id, page=1, limit=DEFAULT_LIMIT),
    )


@pytest.fixture(scope="module")
def first_product_id(api, schemashot, first_category_id) -> int:
    resp = make_test(
        schemashot,
        partial(api.Catalog.category, first_category_id, page=1, limit=1),
    )
    return resp.json()["content"]["items"][0]["id"]


def test_single_product(api, schemashot, first_product_id):
    make_test(schemashot, partial(api.Catalog.product, first_product_id))
