import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT


@pytest.mark.asyncio
async def test_catalog_tree(schemashot: SchemaShot):
    """Тест для получения дерева категорий каталога"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Catalog.tree()
        schemashot.assert_match(handler.response, "catalog_tree")

@pytest.mark.asyncio
async def test_catalog_form(schemashot: SchemaShot):
    """Тест для получения формы каталога с доступными фильтрами"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = 1389
        
        handler = await api.Catalog.form(filter=filter)
        schemashot.assert_match(handler.response, "catalog_form")

@pytest.mark.asyncio
async def test_catalog_feed_with_filters(schemashot: SchemaShot):
    """Тест для получения товаров с различными фильтрами"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = 1389
        filter.ONLY_DISCOUNT = True
        filter.FROM_PEREKRESTOK = True
        filter.set_price_range(1000, 50000)  # цены в копейках
        
        catalog_handler = await api.Catalog.feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        schemashot.assert_match(catalog_handler.response, "catalog_feed_filtered")

        if catalog_handler.response["content"]["items"]:
            product_id = catalog_handler.response["content"]["items"][0]["id"]
            
            handler = await api.Catalog.product(product_id)
            schemashot.assert_match(handler.response, "product_info")

@pytest.mark.asyncio
async def test_promo_listings_by_id(schemashot: SchemaShot):
    """Тест для получения промо-листов по ID"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Пробуем несколько ID промо-листов
        promo_ids = [1, 2, 3, 4, 5]
        handler = await api.Catalog.promo_listings_by_id(promo_ids)
        schemashot.assert_match(handler.response, "promo_listings_by_id")
