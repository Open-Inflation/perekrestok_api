import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI
from conftest import is_not_error


class TestGeneralFlow:
    """Класс для тестирования общих функций"""
    
    @pytest.mark.dependency()
    def test_qualifier(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.General.qualifier()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "ClassGeneral.qualifier.main")

    @pytest.mark.dependency()
    def test_feedback_form(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.General.feedback_form()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "ClassGeneral.feedback_form")

    @pytest.mark.dependency()
    def test_delivery_switcher(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.General.delivery_switcher()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "ClassGeneral.delivery_switcher")

    @pytest.mark.dependency()
    def test_current_user(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.General.current_user()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "ClassGeneral.current_user")

    @pytest.mark.dependency()
    def test_download_image(self, api: PerekrestokAPI):
        image_url = "https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/files/ae/2a/4f39b2a249768b268ed9f325c155.png"
        image_resp = api.General.download_image(image_url)
        image_data = image_resp.content

        assert isinstance(image_data, bytes)
        assert len(image_data) > 0
        assert image_data[:8] == b'\x89PNG\r\n\x1a\n'
