from . import abstraction as ABSTRACT
from rich.console import Console
from standard_open_inflation_package import BaseAPI, Page, Request, Response
from standard_open_inflation_package.handler import Handler, HandlerSearchFailed, HandlerSearchSuccess, ExpectedContentType
from standard_open_inflation_package.models import HttpMethod, Cookie
from standard_open_inflation_package.content_loader import _remove_csrf_prefixes
import json
from io import BytesIO


CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"{MAIN_SITE_URL}/api/customer/{CATALOG_VERSION}"


class PerekrestokAPI:
    def __init__(self, debug: bool = False, **kwargs):
        self.BROWSER = BaseAPI(start_func=self._start_browser, request_modifier_func=self._request_modifier, **kwargs)
        self.PAGE = None
        
        self._geolocation = self._ClassGeolocation(parent=self)
        self._catalog = self._ClassCatalog(parent=self)
        self._general = self._ClassGeneral(parent=self)
        self._advertising = self._ClassAdvertising(parent=self)

    async def __aenter__(self):
        await self.rebuild_connection()
        return self

    async def rebuild_connection(self):
        await self.BROWSER.new_session()

    async def _start_browser(self, browser: BaseAPI):
        self.PAGE = await browser.new_page()
        resp = await self.PAGE.direct_fetch(
            url=MAIN_SITE_URL,
            handlers=Handler.MAIN(expected_content=ExpectedContentType.ANY),
            wait_selector="div#app"
        )
    
    async def _request_modifier(self, req: Request) -> Request:
        """
        Модифицирует запросы перед отправкой.
        Здесь можно добавить куки, заголовки и тп.
        """
        
        cookies = await self.PAGE.get_cookies()
        
        for cookie in cookies:
            if cookie.name == "session":
                clean_json = json.loads(_remove_csrf_prefixes(cookie.value))

                req.add_header("Auth", f"Bearer {clean_json['accessToken']}")

                break
        else:
            raise ValueError("Session cookie not found in cookies")

        return req


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.BROWSER.close()

    class _ClassGeolocation:
        def __init__(self, parent):
            self._parent = parent
            self._selection = self._GeolocationSelection(parent=self._parent)
            self._shop_service = self._ShopService(parent=self._parent)

        async def current(self):
            """
            Получает информацию о текущем городе (геолокация).
            Судя по всему определение по IP не происходит, и анонимный пользователь всегда "находится" в Москве.
            Если подгрузились с анонимного токена и там был сменён город - решение сохранится.
            """
            url = f"{CATALOG_URL}/geo/city/current"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def delivery_address(self):
            """
            Возвращает список всех адресов доставки которые пользователь когда-либо указывал (заказывать на него не обязательно).
            """
            url = f"{CATALOG_URL}/delivery/address"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def search(self, search: str, limit: int = 40):
            """
            Ищет города по названию.
            """
            url = f"{CATALOG_URL}/geo/city?search={search}&limit={limit}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response


        class _ShopService:
            def __init__(self, parent):
                self._parent = parent

            async def all(self):
                """
                Возвращает id-список абсолютно всех магазинов, геолокацию и сводную информацию по ним. 
                Выдача не зависит от геопозиции сессии.
                """
                url = f"{CATALOG_URL}/shop/points"
                response = await self._parent.PAGE.inject_fetch(url)
                return response

            async def info(self, shop_id: int):
                """
                Возвращает информацию о магазине.
                """
                url = f"{CATALOG_URL}/shop/{shop_id}"
                response = await self._parent.PAGE.inject_fetch(url)
                return response
            
            async def on_map(
                    self,
                    position: ABSTRACT.Geoposition = None,
                    page: int = 1,
                    limit: int = 10,
                    city_id: int = None,
                    sort: ABSTRACT.GeologicationPointSort = ABSTRACT.GeologicationPointSort.Distance.ASC,
                    features: list[int] = []
                ):
                """
                Возвращает список самых ближайших/дальних магазинов от указанной геопозиции.

                latitude, longitude: широта и долгота. Не забывайте, что все геопозиции от сервера всегда идут как `[долгота, широта]`.
                """
                url = f"{CATALOG_URL}/shop?orderBy={sort['orderBy']}&orderDirection={sort['orderDirection']}&page={page}&perPage={limit}"
                if city_id:
                    url += f"&cityId={city_id}"
                if isinstance(position, ABSTRACT.Geoposition):
                    url += f"&lat={position.latitude}&lng={position.longitude}"
                
                if features:
                    url += f"&{'&'.join([f'features[]={feature}' for feature in features])}"

                return await self._parent.PAGE.inject_fetch(url)
            
            async def features(self):
                """
                Возвращает список всех возможных особенностей магазинов.
                """
                url = f"{CATALOG_URL}/shop/features"
                return await self._parent.PAGE.inject_fetch(url)

        class _GeolocationSelection:
            def __init__(self, parent):
                self._parent = parent

            async def shop(self, shop_id: int):
                """
                Переключает на выбранный магазин (содержание каталога изменится).
                """
                url = f"{CATALOG_URL}/delivery/mode/pickup/{shop_id}"
                request = Request(url=url, method=HttpMethod.PUT)
                response = await self._parent.PAGE.inject_fetch(request)
                return response
            
            async def delivery_point(self, position: ABSTRACT.Geoposition):
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
                            position.longitude,
                            position.latitude
                        ],
                        "type": "Point"
                    }
                }

                response = await self._parent.PAGE.inject_fetch(Request(url=url, method=HttpMethod.POST, body=body))
                return response

        @property
        def Selection(self):
            """
            Переключаем геолокацию и способ доставки (целом для текущей сессии).
            
            Если желаемый магазин/точка доставки не доступен, то сохраняется предыдущая геолокация (просто не происходит переключения).
            """
            return self._selection
        
        @property
        def Shop(self):
            """Поиск магазинов и информации по ним."""
            return self._shop_service


    class _ClassCatalog: # Содержит самое интересное и полезное, что есть в этой библиотеке :)
        def __init__(self, parent):
            self._parent = parent

        async def promo_listings_by_id(self, ids: list[int]):
            """
            Возвращает информацию о промо-листах по переданным ID.
            Эти же листы можно использовать фильтром в `ABSTRACT.CatalogFeedFilter.PROMO_LISTING = int`.
            Я не нашел способа получения списка доступных ID (кроме простого перебора).
            """
            url = f"{CATALOG_URL}/catalog/promo/listings/by-id{'&'.join([f'ids[]={id}' for id in ids])}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def feed(
                self,
                filter: ABSTRACT.CatalogFeedFilter, 
                sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
                page: int = 1, 
                limit: int = 100, 
                with_best_reviews_only: bool = False
            ):
            """
            Возвращает сам список товаров по фильтрам и сортировке.
            """
            url = f"{CATALOG_URL}/catalog/product/feed"
            body = {
                "filter": filter.as_dict(),
                "page": page,
                "perPage": limit,
                "withBestProductReviews": with_best_reviews_only
            }
            body.update(sort)

            response = await self._parent.PAGE.inject_fetch(Request(url=url, method=HttpMethod.POST, body=body))
            return response

        async def product(self, product_id: int | str):
            """
            Возвращает информацию о товаре по его PLU (ID товара).
            """
            if isinstance(product_id, int) or isinstance(product_id, str):
                if not isinstance(product_id, str) or not product_id.startswith("plu"):
                    product_id = f"plu{product_id}"
            else:
                raise TypeError("ID товара должен быть int или str.")
            
            if not product_id.removeprefix("plu").isdigit():
                raise ValueError("ID товара должен быть int или str структуры pluXXX.")

            url = f"{CATALOG_URL}/catalog/product/{product_id}"

            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def form(
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
            response = await self._parent.PAGE.inject_fetch(Request(url=url, method=HttpMethod.POST, body=body))
            return response

        async def tree(self):
            """
            Возвращает полное дерево каталога (структуру категорий и подкатегорий).
            """
            url = f"{CATALOG_URL}/catalog/tree"
            response = await self._parent.PAGE.inject_fetch(Request(url=url, method=HttpMethod.POST))
            return response

    class _ClassAdvertising:
        def __init__(self, parent):
            self._parent = parent

        async def banner(self, places: list[ABSTRACT.BannerPlace]):
            """
            Получает баннеры для указанных мест.
            """
            url = f"{CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def main_slider(self, page: int = 1, limit: int = 10):
            """
            Получает рекламные объявления на категории брендов.
            """
            url = f"{CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response
        
        async def booklet(self, city: int = 81):
            """
            Возвращает спец. категории по типу "суперцена" для города.
            """
            url = f"{CATALOG_URL}/booklet?city={city}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def view_booklet(self, booklet_id: int):
            """
            Просмотр спец. категории с PDF файлом с акцией.
            """
            url = f"{CATALOG_URL}/booklet/{booklet_id}"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

    class _ClassGeneral:
        def __init__(self, parent):
            self._parent = parent

        async def download_image(self, url: str) -> BytesIO:
            """Скачать изображение с сайта."""
            return await self._parent.PAGE.inject_fetch(url)

        async def qualifier(self):
            """
            Отправляет запрос для получения данных по квалификатору.
            """
            url = f"{CATALOG_URL}/qualifier"
            response = await self._parent.PAGE.inject_fetch(Request(url=url, method=HttpMethod.POST))
            return response

        async def feedback_form(self):
            """
            Возвращает JSON структуру с информацией о форме обратной связи.
            """
            url = f"{CATALOG_URL}/feedback/form"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

        async def delivery_switcher(self):
            """
            Получает переключатель доставки.
            """
            url = f"{CATALOG_URL}/delivery/switcher"
            response = await self._parent.PAGE.inject_fetch(url)
            return response
        
        async def current_user(self):
            """
            Получает информацию о текущем пользователе.
            """
            url = f"{CATALOG_URL}/user/current"
            response = await self._parent.PAGE.inject_fetch(url)
            return response

    @property
    def Geolocation(self):
        """Работа с геолокацией пользователя, инструментарий для поиска магазинов и их выбором."""
        return self._geolocation

    @property
    def Catalog(self):
        """Получение каталога."""
        return self._catalog

    @property
    def Advertising(self):
        """Получение рекламных объявлений."""
        return self._advertising

    @property
    def General(self):
        """Загрузка изображений, получение статических форм, информации о пользователе."""
        return self._general
