"""Геолокация"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import quote

from human_requests import autotest
from human_requests.abstraction import FetchResponse, HttpMethod

from .. import abstraction
from ..api_base import ApiChild, ApiParent, api_child_field

if TYPE_CHECKING:
    from ..manager import PerekrestokAPI


@dataclass(init=False)
class ClassGeolocation(ApiChild["PerekrestokAPI"], ApiParent):
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    Selection: GeolocationSelection = api_child_field(
        lambda parent: GeolocationSelection(parent.parent)
    )
    """Сервис для выбора точек доставки и магазинов."""

    Shop: ShopService = api_child_field(lambda parent: ShopService(parent.parent))
    """Сервис для работы с информацией о магазинах."""

    def __init__(self, parent: "PerekrestokAPI"):
        super().__init__(parent)
        ApiParent.__post_init__(self)

    @autotest
    async def current(self) -> FetchResponse:
        """Получить информацию о текущем выбранном городе."""
        url = f"{self._parent.CATALOG_URL}/geo/city/current"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
    async def delivery_address(self) -> FetchResponse:
        """Получить настройки адреса доставки."""
        url = f"{self._parent.CATALOG_URL}/delivery/address"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
    async def address_from_position(
        self, position: abstraction.Geoposition
    ) -> FetchResponse:
        """Получить адрес по координатам (обратное геокодирование).

        Args:
            position: Объект с координатами
        """
        url = f"{self._parent.CATALOG_URL}/geocoder/reverse?lat={position.latitude}&lng={position.longitude}"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
    async def suggests(self, search: str) -> FetchResponse:
        """Получить подсказки адресов по поисковому запросу.

        Args:
            search: Текст для поиска адресов
        """
        url = f"{self._parent.CATALOG_URL}/geocoder/suggests?search={quote(search)}"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
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


class ShopService(ApiChild["PerekrestokAPI"]):
    """Сервис для работы с информацией о магазинах."""

    @autotest
    async def all(self) -> FetchResponse:
        """Получить список всех точек магазинов."""
        url = f"{self._parent.CATALOG_URL}/shop/points"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
    async def info(self, shop_id: int) -> FetchResponse:
        """Получить подробную информацию о магазине.

        Args:
            shop_id: ID магазина
        """
        url = f"{self._parent.CATALOG_URL}/shop/{shop_id}"
        return await self._parent._request(HttpMethod.GET, url)

    @autotest
    async def on_map(
        self,
        position: abstraction.Geoposition | None = None,
        page: int = 1,
        limit: int = 10,
        city_id: int | None = None,
        sort: dict[str, str] = abstraction.GeolocationPointSort.Distance.ASC,
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

    @autotest
    async def features(self) -> FetchResponse:
        """Получить список доступных особенностей магазинов для фильтрации."""
        url = f"{self._parent.CATALOG_URL}/shop/features"
        return await self._parent._request(HttpMethod.GET, url)


class GeolocationSelection(ApiChild["PerekrestokAPI"]):
    """Сервис для выбора точек доставки и магазинов."""

    @autotest
    async def shop_point(self, shop_id: int) -> FetchResponse:
        """Выбрать магазин. Изменяет содержимое каталога.

        Args:
            shop_id: ID магазина для установки как точки самовывоза
        """
        url = f"{self._parent.CATALOG_URL}/delivery/mode/pickup/{shop_id}"
        return await self._parent._request(HttpMethod.PUT, url)

    @autotest
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

    @autotest
    async def delivery_info(self, position: abstraction.Geoposition) -> FetchResponse:
        """Получить информацию о доставке для указанных координат.

        Args:
            position: Координаты для получения информации о доставке
        """
        url = f"{self._parent.CATALOG_URL}/delivery/info?lat={position.latitude}&lng={position.longitude}"
        return await self._parent._request(HttpMethod.GET, url)
