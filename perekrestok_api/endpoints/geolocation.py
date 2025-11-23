"""Геолокация"""

from typing import TYPE_CHECKING
from urllib.parse import quote

from human_requests.abstraction import FetchResponse, HttpMethod

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import PerekrestokAPI


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    def __init__(self, parent: "PerekrestokAPI"):
        self._parent: "PerekrestokAPI" = parent

        self.Selection: GeolocationSelection = GeolocationSelection(parent=self._parent)
        """Сервис для выбора точек доставки и магазинов."""

        self.Shop: ShopService = ShopService(parent=self._parent)
        """Сервис для работы с информацией о магазинах."""

    async def current(self) -> FetchResponse:
        """Получить информацию о текущем выбранном городе."""
        url = f"{self._parent.CATALOG_URL}/geo/city/current"
        return await self._parent._request(HttpMethod.GET, url)

    async def delivery_address(self) -> FetchResponse:
        """Получить настройки адреса доставки."""
        url = f"{self._parent.CATALOG_URL}/delivery/address"
        return await self._parent._request(HttpMethod.GET, url)

    async def address_from_position(
        self, position: abstraction.Geoposition
    ) -> FetchResponse:
        """Получить адрес по координатам (обратное геокодирование).

        Args:
            position: Объект с координатами
        """
        url = f"{self._parent.CATALOG_URL}/geocoder/reverse?lat={position.latitude}&lng={position.longitude}"
        return await self._parent._request(HttpMethod.GET, url)

    async def suggests(self, search: str) -> FetchResponse:
        """Получить подсказки адресов по поисковому запросу.

        Args:
            search: Текст для поиска адресов
        """
        url = f"{self._parent.CATALOG_URL}/geocoder/suggests?search={quote(search)}"
        return await self._parent._request(HttpMethod.GET, url)

    async def search(self, search: str, limit: int = 40) -> FetchResponse:
        """Поиск городов по названию.

        Args:
            search: Название города для поиска
            limit: Максимальное количество результатов
        """
        url = (
            f"{self._parent.CATALOG_URL}/geo/city?search={quote(search)}&limit={limit}"
        )
        return await self._parent._request(HttpMethod.GET, url)


class ShopService:
    """Сервис для работы с информацией о магазинах."""

    def __init__(self, parent: "PerekrestokAPI"):
        self._parent: "PerekrestokAPI" = parent

    async def all(self) -> FetchResponse:
        """Получить список всех точек магазинов."""
        url = f"{self._parent.CATALOG_URL}/shop/points"
        return await self._parent._request(HttpMethod.GET, url)

    async def info(self, shop_id: int) -> FetchResponse:
        """Получить подробную информацию о магазине.

        Args:
            shop_id: ID магазина
        """
        url = f"{self._parent.CATALOG_URL}/shop/{shop_id}"
        return await self._parent._request(HttpMethod.GET, url)

    async def on_map(
        self,
        position: abstraction.Geoposition | None = None,
        page: int = 1,
        limit: int = 10,
        city_id: int | None = None,
        sort: abstraction.GeolocationPointSort = abstraction.GeolocationPointSort.Distance.ASC,
        features: list[int] | None = None,
    ) -> FetchResponse:
        """Поиск магазинов на карте с фильтрацией и сортировкой.

        Args:
            position: Координаты для поиска ближайших магазинов
            page: Номер страницы для пагинации
            limit: Количество магазинов на странице
            city_id: ID города для фильтрации
            sort: Сортировка результатов
            features: Список особенностей магазина для фильтрации
        """
        url = f"{self._parent.CATALOG_URL}/shop?orderBy={sort['orderBy']}&orderDirection={sort['orderDirection']}&page={page}&perPage={limit}"
        if city_id:
            url += f"&cityId={city_id}"
        if isinstance(position, abstraction.Geoposition):
            url += f"&lat={position.latitude}&lng={position.longitude}"
        if features:
            url += "&" + "&".join([f"features[]={f}" for f in features])
        return await self._parent._request(HttpMethod.GET, url)

    async def features(self) -> FetchResponse:
        """Получить список доступных особенностей магазинов для фильтрации."""
        url = f"{self._parent.CATALOG_URL}/shop/features"
        return await self._parent._request(HttpMethod.GET, url)


class GeolocationSelection:
    """Сервис для выбора точек доставки и магазинов."""

    def __init__(self, parent: "PerekrestokAPI"):
        self._parent: "PerekrestokAPI" = parent

    async def shop_point(self, shop_id: int) -> FetchResponse:
        """Выбрать магазин. Изменяет содержимое каталога.

        Args:
            shop_id: ID магазина для установки как точки самовывоза
        """
        url = f"{self._parent.CATALOG_URL}/delivery/mode/pickup/{shop_id}"
        return await self._parent._request(HttpMethod.PUT, url)

    async def delivery_point(self, position: abstraction.Geoposition) -> FetchResponse:
        """Установить точку доставки курьером.

        Args:
            position: Координаты точки доставки
        """
        url = f"{self._parent.CATALOG_URL}/delivery/mode/courier"
        body = {
            "apartment": None,
            "location": {
                "coordinates": [position.longitude, position.latitude],
                "type": "Point",
            },
        }
        return await self._parent._request(HttpMethod.POST, url, json_body=body)

    async def delivery_info(self, position: abstraction.Geoposition) -> FetchResponse:
        """Получить информацию о доставке для указанных координат.

        Args:
            position: Координаты для получения информации о доставке
        """
        url = f"{self._parent.CATALOG_URL}/delivery/info?lat={position.latitude}&lng={position.longitude}"
        return await self._parent._request(HttpMethod.GET, url)
