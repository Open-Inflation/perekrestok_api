import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT


@pytest.mark.asyncio
async def test_catalog_tree(schemashot: SchemaShot):
    """Тест для получения дерева категорий каталога"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        resp = await api.Catalog.tree()
        schemashot.assert_match(resp, "catalog_tree")

@pytest.mark.asyncio
async def test_catalog_form(schemashot: SchemaShot):
    """Тест для получения формы каталога с доступными фильтрами"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = 1389

        resp = await api.Catalog.form(filter=filter)
        schemashot.assert_match(resp, "catalog_form")

@pytest.mark.asyncio
async def test_catalog_feed_with_filters(schemashot: SchemaShot):
    """Тест для получения товаров с различными фильтрами"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = 1389
        filter.ONLY_DISCOUNT = True
        filter.FROM_PEREKRESTOK = True
        filter.set_price_range(1000, 50000)  # цены в копейках
        
        catalog_resp = await api.Catalog.feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        schemashot.assert_match(catalog_resp, "catalog_feed_filtered")

        if catalog_resp["content"]["items"]:
            product_id = catalog_resp["content"]["items"][0]["id"]

            resp = await api.Catalog.product(product_id)
            schemashot.assert_match(resp, "product_info")

@pytest.mark.asyncio
async def test_promo_listings_by_id(schemashot: SchemaShot):
    """Тест для получения промо-листов по ID"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Пробуем несколько ID промо-листов
        promo_ids = [1, 2, 3, 4, 5]
        resp = await api.Catalog.promo_listings_by_id(promo_ids)
        schemashot.assert_match(resp, "promo_listings_by_id")
