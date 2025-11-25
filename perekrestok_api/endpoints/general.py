"""Общий (не класифицируемый) функционал"""

from io import BytesIO
from typing import TYPE_CHECKING

from aiohttp_retry import ExponentialRetry, RetryClient
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy

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

    async def download_image(
        self, url: str, retry_attempts: int = 3, timeout: float = 10
    ) -> BytesIO:
        """Скачать изображение по URL."""
        retry_options = ExponentialRetry(
            attempts=retry_attempts, start_timeout=3.0, max_timeout=timeout
        )

        async with RetryClient(retry_options=retry_options) as retry_client:
            async with retry_client.get(
                url, raise_for_status=True, proxy=Proxy(self._parent.proxy).as_str()
            ) as resp:
                body = await resp.read()
                file = BytesIO(body)
                file.name = url.split("/")[-1]
        return file

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
