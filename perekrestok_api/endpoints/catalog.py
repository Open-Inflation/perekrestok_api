from .. import abstraction as ABSTRACT


class ClassCatalog:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL
        self.Product = ProductService(parent=self._parent, CATALOG_URL=CATALOG_URL)

    def category_reviews(self, category_id: int | list[int]):
        """Получить отзывы о товарах в категории или категориях по её ID."""
        url = f"{self.CATALOG_URL}/catalog/category/review/aggregate"
        if isinstance(category_id, int):
            category_id = [category_id]
        return self._parent._request("POST", url, json_body={"categories": category_id})

    def preview_feed(self, category_id: int):
        """Получение превью фида товаров разбитых на подкатегории.
        Работает исключительно с КАТЕГОРИЯМИ, а не с подкатегориями."""
        url = f"{self.CATALOG_URL}/catalog/category/feed/{category_id}"
        return self._parent._request("GET", url)

    def feed(
        self,
        filter: ABSTRACT.CatalogFeedFilter,
        sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
        page: int = 1,
        limit: int = 100,
        with_best_reviews_only: bool = False,
    ):
        """
        Получение фида товаров с фильтрами и сортировкой.
        
        Схема плоской ленты товаров. 
        Все товары находятся на одном уровне без объединения в группы. 
        Используется для простых списков с единым порядком сортировки и пагинацией. 
        Подходит для бесконечной прокрутки, поиска и фильтрации без акцентирования на группах или промоблоках.
        """
        url = f"{self.CATALOG_URL}/catalog/product/feed"
        body = {
            "filter": filter.as_dict(),
            "page": page,
            "perPage": limit,
            "withBestProductReviews": with_best_reviews_only,
        }
        body.update(sort)
        return self._parent._request("POST", url, json_body=body)

    def grouped_feed(
        self,
        filter: ABSTRACT.CatalogFeedFilter,
        sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
        page: int = 1,
        limit: int = 100,
        with_best_reviews_only: bool = False,
    ):
        """
        Получение фида товаров с фильтрами и сортировкой.
        Работает исключительно с ПОДКАТЕГОРИЯМИ, а не с категориями. Использование ID категории приведет к status 400.
        
        Схема ленты с группировкой товаров. 
        Товары объединяются в группы (например, по акции, бренду или категории), каждая с отдельным заголовком и дополнительными данными. 
        Используется для отображения блоков с собственными заголовками, промо, клубными предложениями и акцентами на группах.
        """
        url = f"{self.CATALOG_URL}/catalog/product/grouped-feed"
        body = {
            "filter": filter.as_dict(),
            "page": page,
            "perPage": limit,
            "withBestProductReviews": with_best_reviews_only,
        }
        body.update(sort)
        return self._parent._request("POST", url, json_body=body)

    def form(
        self,
        filter: ABSTRACT.CatalogFeedFilter,
        disable_bubble_up: bool = False,
        sort_by_alpha: bool = True,
    ):
        url = f"{self.CATALOG_URL}/catalog/search/form"
        body = {
            "filter": filter.as_dict(),
            "disableBubbleUp": disable_bubble_up,
            "sortByAlpha": sort_by_alpha,
        }
        return self._parent._request("POST", url, json_body=body)

    def tree(self):
        """Получить дерево категорий каталога."""
        url = f"{self.CATALOG_URL}/catalog/tree"
        return self._parent._request("POST", url)
    
    def category_info(self, category_id: int):
        """Получить информацию о категории по её ID."""
        url = f"{self.CATALOG_URL}/catalog/category/{category_id}/full"
        return self._parent._request("GET", url)

class ProductService:
    """Сервис для работы с товарами в каталоге."""
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL
    
    def _check_plu(self, product_plu: int | str) -> str:
        """Проверка PLU товара на корректность."""
        if isinstance(product_plu, int) or isinstance(product_plu, str):
            if not str(product_plu).startswith("plu"):
                product_plu = f"plu{product_plu}"
        else:
            raise TypeError("ID товара должен быть int или str.")
        if not str(product_plu).removeprefix("plu").isdigit():
            raise ValueError("ID товара должен быть int или str структуры pluXXX.")
        return product_plu

    def info(self, product_plu: int | str):
        """Получить информацию о товаре по PLU! НЕ ПУТАТЬ С ID ТОВАРА!"""
        product_plu = self._check_plu(product_plu)
        url = f"{self.CATALOG_URL}/catalog/product/{product_plu}"
        return self._parent._request("GET", url)

    def available_count(self, product_plu: int | str):
        """Получить информацию о количестве товара в магазинах по PLU! НЕ ПУТАТЬ С ID ТОВАРА!"""
        product_plu = self._check_plu(product_plu)
        url = f"{self.CATALOG_URL}/catalog/{product_plu}/shop-availability/count"
        return self._parent._request("GET", url)

    def similar(self, product_id: int):
        """Получить похожие товары по ID! НЕ ПУТАТЬ С PLU!"""
        url = f"{self.CATALOG_URL}/catalog/product/{product_id}/similar"
        return self._parent._request("GET", url)
    
    def categories(self, product_plu: int | str):
        """Получить списка категорий которым относится товар - по PLU! НЕ ПУТАТЬ С ID ТОВАРА!"""
        product_plu = self._check_plu(product_plu)
        url = f"{self.CATALOG_URL}/catalog/product/{product_plu}/categories"
        return self._parent._request("GET", url)

    def reviews_count(self, product_plu: int | str):
        """Получить количество отзывов о товаре по PLU! НЕ ПУТАТЬ С ID ТОВАРА!"""
        product_plu = self._check_plu(product_plu)
        url = f"{self.CATALOG_URL}/catalog/product/{product_plu}/review/count"
        return self._parent._request("GET", url)

    def reviews(self, product_plu: int | str, page: int = 1, limit: int = 10):
        """Получить отзывы о товаре по PLU! НЕ ПУТАТЬ С ID ТОВАРА!"""
        product_plu = self._check_plu(product_plu)
        url = f"{self.CATALOG_URL}/catalog/product/{product_plu}/review?page={page}&perPage={limit}"
        return self._parent._request("GET", url)
