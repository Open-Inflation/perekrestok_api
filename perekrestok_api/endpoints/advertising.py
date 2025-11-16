"""Реклама"""

from typing import TYPE_CHECKING

from human_requests.abstraction import FetchResponse, HttpMethod

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import PerekrestokAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "PerekrestokAPI"):
        self._parent: "PerekrestokAPI" = parent

    async def banner(self, places: list[abstraction.BannerPlace]) -> FetchResponse:
        """Получить баннеры для указанных мест размещения.

        Args:
            places: Список мест размещения баннеров из BannerPlace
        """
        url = f"{self._parent.CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
        return await self._parent._request(HttpMethod.GET, url)

    async def main_slider(self, page: int = 1, limit: int = 10) -> FetchResponse:
        """Получить элементы главного слайдера.

        Args:
            page: Номер страницы для пагинации
            limit: Количество элементов на странице
        """
        url = f"{self._parent.CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
        return await self._parent._request(HttpMethod.GET, url)

    async def booklet(self, city: int = 81) -> FetchResponse:
        """Получить список доступных буклетов для города.

        Args:
            city: ID города (по умолчанию 81 - Москва)
        """
        url = f"{self._parent.CATALOG_URL}/booklet?city={city}"
        return await self._parent._request(HttpMethod.GET, url)

    async def view_booklet(self, booklet_id: int) -> FetchResponse:
        """Получить содержимое конкретного буклета.

        Args:
            booklet_id: ID буклета для просмотра
        """
        url = f"{self._parent.CATALOG_URL}/booklet/{booklet_id}"
        return await self._parent._request(HttpMethod.GET, url)
