import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT
from conftest import is_not_error


class TestGeolocationFlow:
    """Класс для тестирования геолокации с зависимостями между тестами"""
    
    @pytest.fixture(scope="class")
    def shared_data(self):
        """Хранилище данных для передачи между тестами"""
        return {}

    @pytest.mark.dependency()
    def test_current_geolocation(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.current()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "current_geolocation")

    @pytest.mark.dependency()
    def test_delivery_address(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.delivery_address()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "delivery_address")

    @pytest.mark.dependency()
    def test_delivery_info(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.Selection.delivery_info(ABSTRACT.Geoposition(latitude=55.75582, longitude=37.61729))
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "delivery_info")

    @pytest.mark.dependency()
    def test_address_from_position(self, api: PerekrestokAPI, schemashot: SchemaShot):
        position = ABSTRACT.Geoposition(latitude=55.7558, longitude=37.6176)  # Moscow coordinates
        resp = api.Geolocation.address_from_position(position)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "address_from_position")

    @pytest.mark.dependency()
    def test_geocoder_suggests(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.suggests("москва")
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "geocoder_suggests")

    @pytest.mark.dependency()
    def test_search_geolocation(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.search("москва", limit=5)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "search_geolocation")

    @pytest.mark.dependency()
    def test_get_all_shops(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        shops_resp = api.Geolocation.Shop.all()
        is_not_error(shops_resp)
        shops_resp_data = shops_resp.json()
        schemashot.assert_match(shops_resp_data, "all_shops")
        
        shared_data['shop_id'] = shops_resp_data["content"]["items"][0]["id"]

    @pytest.mark.dependency(depends=["TestGeolocationFlow::test_get_all_shops"])
    def test_shop_info(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        if 'shop_id' not in shared_data:
            pytest.skip("Зависимый тест test_get_all_shops не прошел")

        resp = api.Geolocation.Shop.info(shared_data['shop_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "shop_info")

    @pytest.mark.dependency(depends=["TestGeolocationFlow::test_get_all_shops"])
    def test_select_shop(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        if 'shop_id' not in shared_data:
            pytest.skip("Зависимый тест test_get_all_shops не прошел")

        resp = api.Geolocation.Selection.shop_point(shared_data['shop_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "select_shop")

    @pytest.mark.dependency()
    def test_shops_on_map(self, api: PerekrestokAPI, schemashot: SchemaShot):
        # Moscow coordinates (latitude, longitude)
        position = ABSTRACT.Geoposition(55.7558, 37.6176)
        resp = api.Geolocation.Shop.on_map(
            position=position,
            limit=3,
            sort=ABSTRACT.GeolocationPointSort.Distance.ASC
        )
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "shops_on_map")

    @pytest.mark.dependency()
    def test_shop_features(self, api: PerekrestokAPI, schemashot: SchemaShot):
        resp = api.Geolocation.Shop.features()
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "shop_features")

    @pytest.mark.dependency()
    def test_select_delivery_point(self, api: PerekrestokAPI, schemashot: SchemaShot):
        # Moscow coordinates
        position = ABSTRACT.Geoposition(55.7655519, 37.5916321)
        resp = api.Geolocation.Selection.delivery_point(position)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "select_delivery_point")
