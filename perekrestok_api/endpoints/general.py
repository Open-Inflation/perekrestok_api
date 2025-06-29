"""Общий (не класифицируемый) функционал"""
from .. import abstraction
from hrequests import Response


class ClassGeneral:
    """Общие методы API Перекрёстка.
    
    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def download_image(self, url: str) -> Response:
        """Скачать изображение по URL.
        
        Args:
            url: URL изображения для скачивания
        """
        return self._parent._request("GET", url)

    def qualifier(self, selections: list[abstraction.QualifierFeatureKey] | None = None) -> Response:
        """Получить конфигурацию функций API.
        
        Args:
            selections: Список ключей функций для получения. 
                При None возвращает ответы по всем доступным ключам.
        """
        url = f"{self.CATALOG_URL}/qualifier"
        if selections is None:
            selections = abstraction.QualifierFeatureKey.get_all()
        return self._parent._request("POST", url, json_body={"keys": selections})

    def feedback_form(self) -> Response:
        """Получить форму обратной связи."""
        url = f"{self.CATALOG_URL}/feedback/form"
        return self._parent._request("GET", url)

    def delivery_switcher(self) -> Response:
        """Получить информацию о переключателе доставки."""
        url = f"{self.CATALOG_URL}/delivery/switcher"
        return self._parent._request("GET", url)

    def current_user(self) -> Response:
        """Получить информацию о текущем пользователе."""
        url = f"{self.CATALOG_URL}/user/current"
        return self._parent._request("GET", url)