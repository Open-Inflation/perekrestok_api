import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT


@pytest.mark.asyncio
async def test_banner(schemashot: SchemaShot):
    """Тест для получения баннеров"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        places = [
            ABSTRACT.BannerPlace.MAIN_BANNERS,
            ABSTRACT.BannerPlace.BRANDS,
            ABSTRACT.BannerPlace.CATEGORY
        ]
        handler = await api.Advertising.banner(places)
        schemashot.assert_match(handler.response, "banner")


@pytest.mark.asyncio
async def test_main_slider(schemashot: SchemaShot):
    """Тест для получения главного слайдера"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.Advertising.main_slider(page=1, limit=5)
        schemashot.assert_match(handler.response, "main_slider")


@pytest.mark.asyncio
async def test_booklet_and_view_booklet(schemashot: SchemaShot):
    """Тест для получения буклетов спецкатегорий"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        # Москва - city_id = 81
        booklets_handler = await api.Advertising.booklet(city=81)
        schemashot.assert_match(booklets_handler.response, "booklet")

        if booklets_handler.response["content"]["items"]:
            booklet_id = booklets_handler.response["content"]["items"][0]["id"]
            view_handler = await api.Advertising.view_booklet(booklet_id)
            schemashot.assert_match(view_handler.response, "view_booklet")


@pytest.mark.asyncio
async def test_special_category_banners(schemashot: SchemaShot):
    """Тест для получения баннеров специальных категорий"""
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        places = [
            ABSTRACT.BannerPlace.SpecialCategory.TITLE,
            ABSTRACT.BannerPlace.SpecialCategory.LEFT,
            ABSTRACT.BannerPlace.SpecialCategory.RIGHT
        ]
        handler = await api.Advertising.banner(places)
        schemashot.assert_match(handler.response, "special_category_banners")
