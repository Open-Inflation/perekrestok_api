"""Общий (не класифицируемый) функционал"""

from typing import TYPE_CHECKING

from human_requests.abstraction import FetchResponse, HttpMethod

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import PerekrestokAPI


class ClassGeneral:
    """Общие методы API Перекрёстка.

    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """

    def __init__(self, parent: "PerekrestokAPI"):
        self._parent: "PerekrestokAPI" = parent

    async def download_image(self, url: str) -> FetchResponse:
        """Скачать изображение по URL.

        Args:
            url: URL изображения для скачивания
        """
        return await self._parent._request(HttpMethod.GET, url)

    async def qualifier(
        self, selections: list[abstraction.QualifierFeatureKey] | None = None
    ) -> FetchResponse:
        """Получить конфигурацию функций API.

        Args:
            selections: Список ключей функций для получения.
                При None возвращает ответы по всем доступным ключам.
        """
        url = f"{self._parent.CATALOG_URL}/qualifier"
        if selections is None:
            selections = abstraction.QualifierFeatureKey.get_all()
        return await self._parent._request(
            HttpMethod.POST, url, json_body={"keys": selections}
        )

    async def feedback_form(self) -> FetchResponse:
        """Получить форму обратной связи."""
        url = f"{self._parent.CATALOG_URL}/feedback/form"
        return await self._parent._request(HttpMethod.GET, url)

    async def delivery_switcher(self) -> FetchResponse:
        """Получить информацию о переключателе доставки."""
        url = f"{self._parent.CATALOG_URL}/delivery/switcher"
        return await self._parent._request(HttpMethod.GET, url)

    async def current_user(self) -> FetchResponse:
        """Получить информацию о текущем пользователе."""
        url = f"{self._parent.CATALOG_URL}/user/current"
        return await self._parent._request(HttpMethod.GET, url)
