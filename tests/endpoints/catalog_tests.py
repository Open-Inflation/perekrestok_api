import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT
from conftest import is_not_error


def test_catalog_tree(api: PerekrestokAPI, schemashot: SchemaShot):
    resp = api.Catalog.tree()
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "catalog_tree")

def test_catalog_form(api: PerekrestokAPI, schemashot: SchemaShot):
    filter = ABSTRACT.CatalogFeedFilter()
    filter.CATEGORY_ID = 1389

    resp = api.Catalog.form(filter=filter)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "catalog_form")

def test_catalog_feed_with_filters(api: PerekrestokAPI, schemashot: SchemaShot):
    filter = ABSTRACT.CatalogFeedFilter()
    filter.CATEGORY_ID = 1389
    filter.ONLY_DISCOUNT = True
    filter.FROM_PEREKRESTOK = True
    filter.set_price_range(1000, 50000)  # prices in kopecks

    catalog_resp = api.Catalog.feed(
        filter=filter,
        sort=ABSTRACT.CatalogFeedSort.Price.ASC,
        limit=5
    )
    is_not_error(catalog_resp)
    catalog_resp_data = catalog_resp.json()
    schemashot.assert_match(catalog_resp_data, "catalog_feed_filtered")

    if catalog_resp_data["content"]["items"]:
        product_id = catalog_resp_data["content"]["items"][0]["id"]

        resp = api.Catalog.product(product_id)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "product_info")

def test_promo_listings_by_id(api: PerekrestokAPI, schemashot: SchemaShot):
    # Try several promo list IDs
    promo_ids = [1, 2, 3, 4, 5]
    resp = api.Catalog.promo_listings_by_id(promo_ids)
    is_not_error(resp)
    schemashot.assert_match(resp.json(), "promo_listings_by_id")
