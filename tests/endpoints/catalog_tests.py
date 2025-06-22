import pytest
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI, ABSTRACT
from conftest import is_not_error


class TestCatalogFlow:
    """Класс для тестирования каталога с зависимостями между тестами"""
    
    @pytest.fixture(scope="class")
    def shared_data(self):
        """Хранилище данных для передачи между тестами"""
        return {}

    # Получение дерева категорий

    @pytest.mark.dependency()
    def test_catalog_tree(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        resp = api.Catalog.tree()
        is_not_error(resp)
        resp_data = resp.json()
        schemashot.assert_match(resp_data, "catalog_tree")
        
        shared_data['first_category_id'] = resp_data["content"]["items"][0]["category"]["id"]
        shared_data['first_subcategory_id'] = resp_data["content"]["items"][0]["children"][0]["category"]["id"]

    # Тесты для категорий

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_info(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        if 'first_category_id' not in shared_data:
            pytest.skip("Зависимый тест test_catalog_tree не прошел")
            
        resp = api.Catalog.category_info(shared_data['first_category_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "category_info")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_reviews(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        if 'first_category_id' not in shared_data:
            pytest.skip("Зависимый тест test_catalog_tree не прошел")
            
        resp = api.Catalog.category_reviews(shared_data['first_category_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "category_reviews")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_catalog_form(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        if 'first_category_id' not in shared_data:
            pytest.skip("Зависимый тест test_catalog_tree не прошел")
            
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = shared_data['first_category_id']

        resp = api.Catalog.form(filter=filter)
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "category_catalog_form")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_catalog_grouped_feed_should_fail(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = shared_data['first_category_id']

        catalog_resp = api.Catalog.grouped_feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        # Assert Error
        with pytest.raises(AssertionError):
            is_not_error(catalog_resp)

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_catalog_feed(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = shared_data['first_category_id']

        catalog_resp = api.Catalog.feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        is_not_error(catalog_resp)
        catalog_resp_data = catalog_resp.json()
        schemashot.assert_match(catalog_resp_data, "category_catalog_feed_filtered")
        
        shared_data['product_id'] = catalog_resp_data["content"]["items"][0]["id"]
        shared_data['product_plu'] = catalog_resp_data["content"]["items"][0]["masterData"]["plu"]

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_category_preview_feed(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        resp = api.Catalog.preview_feed(shared_data['first_category_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "category_preview_feed")

    # Тесты для продуктов

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_category_catalog_feed"])
    def test_product_info(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        resp = api.Catalog.product(shared_data['product_plu'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "product_info")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_category_catalog_feed"])
    def test_product_similar(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        resp = api.Catalog.product_similar(shared_data['product_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "product_similar")

    # Тесты для подкатегорий
    
    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_subcategory_info(self, api: PerekrestokAPI, shared_data, schemashot: SchemaShot):
        resp = api.Catalog.category_info(shared_data['first_subcategory_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "subcategory_info")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_subcategory_reviews(self, api: PerekrestokAPI, shared_data, schemashot: SchemaShot):
        resp = api.Catalog.category_reviews(shared_data['first_subcategory_id'])
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "subcategory_reviews")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_subcategory_catalog_grouped_feed(self, api: PerekrestokAPI, shared_data, schemashot: SchemaShot):
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = shared_data['first_subcategory_id']

        resp = api.Catalog.grouped_feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "subcategory_catalog_grouped_feed_filtered")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_subcategory_catalog_feed(self, api: PerekrestokAPI, shared_data, schemashot: SchemaShot):
        filter = ABSTRACT.CatalogFeedFilter()
        filter.CATEGORY_ID = shared_data['first_subcategory_id']

        resp = api.Catalog.feed(
            filter=filter,
            sort=ABSTRACT.CatalogFeedSort.Price.ASC,
            limit=5
        )
        is_not_error(resp)
        schemashot.assert_match(resp.json(), "subcategory_catalog_feed_filtered")

    @pytest.mark.dependency(depends=["TestCatalogFlow::test_catalog_tree"])
    def test_subcategory_preview_feed_should_fail(self, api: PerekrestokAPI, schemashot: SchemaShot, shared_data):
        resp = api.Catalog.preview_feed(shared_data['first_subcategory_id'])
        with pytest.raises(AssertionError):   
            is_not_error(resp)
