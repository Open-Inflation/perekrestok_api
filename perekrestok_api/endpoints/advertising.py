"""Реклама"""
from .. import abstraction
from hrequests import Response


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.
    
    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def banner(self, places: list[abstraction.BannerPlace]) -> Response:
        """Получить баннеры для указанных мест размещения.
        
        Args:
            places: Список мест размещения баннеров из BannerPlace
        """
        url = f"{self.CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
        return self._parent._request("GET", url)

    def main_slider(self, page: int = 1, limit: int = 10) -> Response:
        """Получить элементы главного слайдера.
        
        Args:
            page: Номер страницы для пагинации
            limit: Количество элементов на странице
        """
        url = f"{self.CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
        return self._parent._request("GET", url)

    def booklet(self, city: int = 81) -> Response:
        """Получить список доступных буклетов для города.
        
        Args:
            city: ID города (по умолчанию 81 - Москва)
        """
        url = f"{self.CATALOG_URL}/booklet?city={city}"
        return self._parent._request("GET", url)

    def view_booklet(self, booklet_id: int) -> Response:
        """Получить содержимое конкретного буклета.
        
        Args:
            booklet_id: ID буклета для просмотра
        """
        url = f"{self.CATALOG_URL}/booklet/{booklet_id}"
        return self._parent._request("GET", url)
