from . import abstraction as ABSTRACT
from .api import BaseAPI
from rich.console import Console


CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"/api/customer/{CATALOG_VERSION}"


class PerekrestokAPI:
    def __init__(self, debug: bool = False, token_retry_attempts: int = 3):
        self.debug = debug
        self._token_retry_attempts = token_retry_attempts

        self.console = Console()
        self._fetcher = BaseAPI(base_url=MAIN_SITE_URL, debug=debug, console=self.console)

        self._geo = self._ClassGEO(fetcher=self._fetcher)
        self._catalog = self._ClassCatalog(fetcher=self._fetcher)
        self._general = self._ClassGeneral(fetcher=self._fetcher)
        self._advertising = self._ClassAdvertising(fetcher=self._fetcher)

    async def __aenter__(self):
        for _ in range(self._token_retry_attempts):
            await self._fetcher.__aenter__()
            if self._fetcher.cookies.get("session"):
                if self.debug: self.console.log('[bold green]Session tokens found.[/bold green]')
                break
            
            if self.debug: self.console.log('[bold yellow]Session tokens not found. Retrying...[/bold yellow]')
        else:
            raise Exception("Failed to get session token")
        if self.debug: self.console.log("")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._fetcher.__aexit__(exc_type, exc_val, exc_tb)

    class _ClassGEO:
        def __init__(self, fetcher):
            self._fetcher = fetcher

        async def current(self):
            """
            Получает информацию о текущем городе (геолокация).
            """
            url = f"{CATALOG_URL}/geo/city/current"
            response = await self._fetcher.fetch(url)
            return response

        async def search(self, search: str, limit: int = 40):
            """
            Ищет города по названию.
            """
            url = f"{CATALOG_URL}/geo/city?search={search}&limit={limit}"
            response = await self._fetcher.fetch(url)
            return response

        async def shop_points(self):
            """
            Возвращает точки продаж (геолокация).
            """
            url = f"{CATALOG_URL}/shop/points"
            response = await self._fetcher.fetch(url)
            return response

    class _ClassCatalog:
        def __init__(self, fetcher):
            self._fetcher = fetcher

        async def promo_listings_by_id(self, ids: list[int]):
            """
            Возвращает промо-листы по переданным ID.
            """
            url = f"{CATALOG_URL}/catalog/promo/listings/by-id{'&'.join([f'ids[]={id}' for id in ids])}"
            response = await self._fetcher.fetch(url)
            return response

        async def product_feed(
                self,
                filter: ABSTRACT.CatalogFeedFilter, 
                sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
                page: int = 1, 
                limit: int = 100, 
                best_product_reviews_only: bool = False
            ):
            """
            Возвращает сам список товаров по фильтрам и сортировке.
            """
            url = f"{CATALOG_URL}/catalog/product/feed"
            body = {
                "filter": filter.as_dict(),
                "page": page,
                "perPage": limit,
                "withBestProductReviews": best_product_reviews_only
            }
            body.update(sort)

            response = await self._fetcher.fetch(url, method="POST", body=body)
            return response

        async def search_form(
                self,
                disable_bubble_up: bool = False,
                sort_by_alpha: bool = True
            ):
            """
            Возвращает структуру доступной для поиска информации.
            """
            url = f"{CATALOG_URL}/catalog/search/form"
            body = {
                "disableBubbleUp": disable_bubble_up,
                "sortByAlpha": sort_by_alpha
            }
            response = await self._fetcher.fetch(url, method="POST", body=body)
            return response

        async def tree(self):
            """
            Возвращает полное дерево каталога.
            """
            url = f"{CATALOG_URL}/catalog/tree"
            response = await self._fetcher.fetch(url, method="POST")
            return response

    class _ClassAdvertising:
        def __init__(self, fetcher):
            self._fetcher = fetcher

        async def banner(self, places: list[ABSTRACT.BannerPlace]):
            """
            Получает баннеры для указанных мест.
            """
            url = f"{CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
            response = await self._fetcher.fetch(url)
            return response

        async def main_slider(self, page: int = 1, limit: int = 10):
            """
            Получает рекламные объявления на категории брендов.
            """
            url = f"{CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
            response = await self._fetcher.fetch(url)
            return response
        
        async def booklet(self, city: int = 81):
            """
            Возвращает спец. категории по типу "суперцена" для города.
            """
            url = f"{CATALOG_URL}/booklet?city={city}"
            response = await self._fetcher.fetch(url)
            return response

        async def view_booklet(self, booklet_id: int):
            """
            Просмотр спец. категории с PDF файлом с акцией.
            """
            url = f"{CATALOG_URL}/booklet/{booklet_id}"
            response = await self._fetcher.fetch(url)
            return response

    class _ClassGeneral:
        def __init__(self, fetcher):
            self._fetcher = fetcher

        async def qualifier(self):
            """
            Отправляет запрос для получения данных по квалификатору.
            """
            url = f"{CATALOG_URL}/qualifier"
            response = await self._fetcher.fetch(url, method="POST")
            return response

        async def feedback_form(self):
            """
            Возвращает JSON структуру с информацией о форме обратной связи.
            """
            url = f"{CATALOG_URL}/feedback/form"
            response = await self._fetcher.fetch(url)
            return response

        async def delivery_switcher(self):
            """
            Получает переключатель доставки.
            """
            url = f"{CATALOG_URL}/delivery/switcher"
            response = await self._fetcher.fetch(url)
            return response
        
        async def current_user(self):
            """
            Получает информацию о текущем пользователе.
            """
            url = f"{CATALOG_URL}/user/current"
            response = await self._fetcher.fetch(url)
            return response

    @property
    def GEO(self):
        return self._geo

    @property
    def Catalog(self):
        return self._catalog

    @property
    def Advertising(self):
        return self._advertising

    @property
    def General(self):
        return self._general
