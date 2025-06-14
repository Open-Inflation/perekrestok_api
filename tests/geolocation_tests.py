import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT


@pytest.mark.asyncio
async def test_current_geolocation(schemashot: SchemaShot):
    """Тест для получения текущей геолокации"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Geolocation.current()
        schemashot.assert_match(handler.response, "current_geolocation")

@pytest.mark.asyncio
async def test_delivery_address(schemashot: SchemaShot):
    """Тест для получения адресов доставки"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Geolocation.delivery_address()
        schemashot.assert_match(handler.response, "delivery_address")

@pytest.mark.asyncio
async def test_search_geolocation(schemashot: SchemaShot):
    """Тест для поиска городов по названию"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Geolocation.search("москва", limit=5)
        schemashot.assert_match(handler.response, "search_geolocation")

@pytest.mark.asyncio
async def test_get_all_shops_and_shop_info(schemashot: SchemaShot):
    """Тест для получения информации о конкретном магазине"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Сначала получаем список магазинов, чтобы взять ID
        shops_handler = await api.Geolocation.Shop.all()
        schemashot.assert_match(shops_handler.response, "all_shops")
        shop_id = shops_handler.response["content"]["items"][0]["id"]
        
        handler = await api.Geolocation.Shop.info(shop_id)
        schemashot.assert_match(handler.response, "shop_info")
        
        handler = await api.Geolocation.Selection.shop(shop_id)
        schemashot.assert_match(handler.response, "select_shop")


@pytest.mark.asyncio
async def test_shops_on_map(schemashot: SchemaShot):
    """Тест для поиска магазинов на карте"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Координаты Москвы (широта, долгота)
        position = ABSTRACT.Geoposition(55.7558, 37.6176)
        handler = await api.Geolocation.Shop.on_map(
            position=position,
            limit=3,
            sort=ABSTRACT.GeologicationPointSort.Distance.ASC
        )
        schemashot.assert_match(handler.response, "shops_on_map")


@pytest.mark.asyncio
async def test_shop_features(schemashot: SchemaShot):
    """Тест для получения особенностей магазинов"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Geolocation.Shop.features()
        schemashot.assert_match(handler.response, "shop_features")


@pytest.mark.asyncio
async def test_select_delivery_point(schemashot: SchemaShot):
    """Тест для выбора точки доставки"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Координаты Москвы
        position = ABSTRACT.Geoposition(55.7558, 37.6176)
        handler = await api.Geolocation.Selection.delivery_point(position)
        schemashot.assert_match(handler.response, "select_delivery_point")
