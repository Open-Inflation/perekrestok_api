import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT
from conftest import is_not_error


class TestAdvertisingFlow:
    """Класс для тестирования рекламы с зависимостями между тестами"""
    
    @pytest.fixture(scope="class")
    def shared_data(self):
        """Хранилище данных для передачи между тестами"""
        return {}

    @pytest.mark.dependency()
    def test_banner(self, api: PerekrestokAPI, schemashot: SchemaShot):
        places = [
            ABSTRACT.BannerPlace.MAIN_BANNERS,
            ABSTRACT.BannerPlace.BRANDS,
            ABSTRACT.BannerPlace.CATEGORY
        ]
        resp = api.Advertising.banner(places)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "banner")

    @pytest.mark.dependency()
    def test_main_slider(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Advertising.main_slider(page=1, limit=5)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "main_slider")

    @pytest.mark.dependency()
    def test_booklet(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        # Moscow - city_id = 81
        booklets_resp = api.Advertising.booklet(city=81)
        is_not_error(booklets_resp)
        booklets_resp_data = booklets_resp.json()
        schemashot.assert_match(booklets_resp_data, "booklet")

        shared_data['booklet_id'] = booklets_resp_data["content"]["items"][0]["id"]

    @pytest.mark.dependency(depends=["TestAdvertisingFlow::test_booklet"])
    def test_view_booklet(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        view_resp = api.Advertising.view_booklet(shared_data['booklet_id'])
        is_not_error(view_resp)
        schemashot.assert_match(view_resp.json(), "view_booklet")

    @pytest.mark.dependency()
    def test_special_category_banners(self, api: PerekrestokAPI, schemashot: SchemaShot):
        places = [
            ABSTRACT.BannerPlace.SpecialCategory.TITLE,
            ABSTRACT.BannerPlace.SpecialCategory.LEFT,
            ABSTRACT.BannerPlace.SpecialCategory.RIGHT
        ]
        resp = api.Advertising.banner(places)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "special_category_banners")
