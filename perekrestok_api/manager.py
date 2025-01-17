from . import abstraction as ABSTRACT
from .api import BaseAPI, ImageDownloader
from rich.console import Console
from io import BytesIO


CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"/api/customer/{CATALOG_VERSION}"


class PerekrestokAPI:
    def __init__(self, debug: bool = False, token_retry_attempts: int = 3):
        self.debug = debug
        self._token_retry_attempts = token_retry_attempts

        self.console = Console()
        self._fetcher = BaseAPI(base_url=MAIN_SITE_URL, debug=debug, console=self.console)
        self._img_downloader = ImageDownloader()

        self._geolocation = self._ClassGeolocation(fetcher=self._fetcher)
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

    class _ClassGeolocation:
        def __init__(self, fetcher):
            self._fetcher = fetcher
            self._selection = self._GeolocationSelection(fetcher=self._fetcher)

        async def current(self):
            """
            Получает информацию о текущем городе (геолокация).
            Судя по всему определение по IP не происходит, и анонимный пользователь всегда "находится" в Москве.
            """
            url = f"{CATALOG_URL}/geo/city/current"
            response = await self._fetcher.fetch(url)
            return response

        async def delivery_address(self):
            """
            Возвращает список всех адресов доставки которые пользователь когда-либо указывал (заказывать на него не обязательно).
            """
            url = f"{CATALOG_URL}/delivery/address"
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
            Возвращает id-список абсолютно всех магазинов, геолокацию и сводную информацию по ним. 
            Выдача не зависит от геопозиции сессии.
            """
            url = f"{CATALOG_URL}/shop/points"
            response = await self._fetcher.fetch(url)
            return response

        async def shop(self, shop_id: int):
            """
            Возвращает информацию о магазине.
            """
            url = f"{CATALOG_URL}/shop/{shop_id}"
            response = await self._fetcher.fetch(url)
            return response

        class _GeolocationSelection:
            """Переключаем геолокацию и способ доставки (целом для текущей сессии)."""

            def __init__(self, fetcher):
                self._fetcher = fetcher

            async def shop(self, shop_id: int):
                """
                Переключает на выбранный магазин (содержание каталога изменится).
                """
                url = f"{CATALOG_URL}/delivery/mode/pickup/{shop_id}"
                response = await self._fetcher.fetch(url, method="PUT")
                return response
            
            async def delivery_point(self, latitude: float, longitude: float):
                """
                Переключает на доставку. Скорее всего после переключения показывается каталог ближайшего магазина (явно не указывается).

                latitude - широта
                longitude - долгота
                """
                url = f"{CATALOG_URL}/delivery/mode/courier"
                body = {
                    "apartment": None,
                    "location": {
                        "coordinates": [ # По какой-то причине в API широта и долгота перепутаны
                            longitude,
                            latitude
                        ],
                        "type": "Point"
                    }
                }

                response = await self._fetcher.fetch(url, method="POST", body=body)
                return response

        @property
        def Selection(self):
            """Если желаемый магазин/точка доставки не доступен, то сохраняется предыдущая геолокация (просто не происходит переключения)."""
            return self._selection


    class _ClassCatalog: # Содержит самое интересное и полезное, что есть в этой библиотеке :)
        def __init__(self, fetcher):
            self._fetcher = fetcher

        async def promo_listings_by_id(self, ids: list[int]):
            """
            Возвращает информацию о промо-листах по переданным ID.
            Эти же листы можно использовать фильтром в `ABSTRACT.CatalogFeedFilter.PROMO_LISTING = int`.
            Я не нашел способа получения списка доступных ID (кроме простого перебора).
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
                filter: ABSTRACT.CatalogFeedFilter, 
                disable_bubble_up: bool = False,
                sort_by_alpha: bool = True
            ):
            """
            Показывает сколько товаров соответсвует запрошенным фильтрам.
            Так же возвращает структуру с информацией о доступных фильтрах (ценовой диапазон, "особенности"),
            предлагаемых способах сортировки и информацию о наличии товаров с ограничением по возрасту (по категориям табак, алкоголь, взрослый контент и тп.).
            
            sortByAlpha - сортировка по алфавиту.
            disableBubbleUp - мне не известно назначение фильтра, по моим наблюдениям всегда передают false.
            """
            url = f"{CATALOG_URL}/catalog/search/form"
            body = {
                "filter": filter.as_dict(),
                "disableBubbleUp": disable_bubble_up,
                "sortByAlpha": sort_by_alpha
            }
            response = await self._fetcher.fetch(url, method="POST", body=body)
            return response

        async def tree(self):
            """
            Возвращает полное дерево каталога (структуру категорий и подкатегорий).
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
    def Geolocation(self):
        return self._geolocation

    @property
    def Catalog(self):
        return self._catalog

    @property
    def Advertising(self):
        return self._advertising

    @property
    def General(self):
        return self._general

    async def download_image(self, url: str) -> BytesIO:
        return await self._img_downloader.download_image(url)
