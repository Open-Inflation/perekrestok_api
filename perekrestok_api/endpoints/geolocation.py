"""Геолокация"""
from .. import abstraction
from hrequests import Response


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.
    
    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.Selection = GeolocationSelection(parent=self._parent, CATALOG_URL=CATALOG_URL)
        """Доступ к методам выбора точек доставки и магазинов."""
        self.Shop = ShopService(parent=self._parent, CATALOG_URL=CATALOG_URL)
        """Доступ к методам работы с магазинами."""
        self.CATALOG_URL = CATALOG_URL

    def current(self) -> Response:
        """Получить информацию о текущем выбранном городе."""
        url = f"{self.CATALOG_URL}/geo/city/current"
        return self._parent._request("GET", url)

    def delivery_address(self) -> Response:
        """Получить настройки адреса доставки."""
        url = f"{self.CATALOG_URL}/delivery/address"
        return self._parent._request("GET", url)

    def address_from_position(self, position: abstraction.Geoposition) -> Response:
        """Получить адрес по координатам (обратное геокодирование).
        
        Args:
            position: Объект с координатами
        """
        url = f"{self.CATALOG_URL}/geocoder/reverse?lat={position.latitude}&lng={position.longitude}"
        return self._parent._request("GET", url)

    def suggests(self, search: str) -> Response:
        """Получить подсказки адресов по поисковому запросу.
        
        Args:
            search: Текст для поиска адресов
        """
        url = f"{self.CATALOG_URL}/geocoder/suggests?search={search}"
        return self._parent._request("GET", url)

    def search(self, search: str, limit: int = 40) -> Response:
        """Поиск городов по названию.
        
        Args:
            search: Название города для поиска
            limit: Максимальное количество результатов
        """
        url = f"{self.CATALOG_URL}/geo/city?search={search}&limit={limit}"
        return self._parent._request("GET", url)

class ShopService:
    """Сервис для работы с информацией о магазинах."""
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def all(self) -> Response:
        """Получить список всех точек магазинов."""
        url = f"{self.CATALOG_URL}/shop/points"
        return self._parent._request("GET", url)

    def info(self, shop_id: int) -> Response:
        """Получить подробную информацию о магазине.
        
        Args:
            shop_id: ID магазина
        """
        url = f"{self.CATALOG_URL}/shop/{shop_id}"
        return self._parent._request("GET", url)

    def on_map(
        self,
        position: abstraction.Geoposition | None = None,
        page: int = 1,
        limit: int = 10,
        city_id: int | None = None,
        sort: abstraction.GeolocationPointSort = abstraction.GeolocationPointSort.Distance.ASC,
        features: list[int] | None = None,
    ) -> Response:
        """Поиск магазинов на карте с фильтрацией и сортировкой.
        
        Args:
            position: Координаты для поиска ближайших магазинов
            page: Номер страницы для пагинации
            limit: Количество магазинов на странице
            city_id: ID города для фильтрации
            sort: Сортировка результатов
            features: Список особенностей магазина для фильтрации
        """
        url = f"{self.CATALOG_URL}/shop?orderBy={sort['orderBy']}&orderDirection={sort['orderDirection']}&page={page}&perPage={limit}"
        if city_id:
            url += f"&cityId={city_id}"
        if isinstance(position, abstraction.Geoposition):
            url += f"&lat={position.latitude}&lng={position.longitude}"
        if features:
            url += "&" + "&".join([f"features[]={f}" for f in features])
        return self._parent._request("GET", url)

    def features(self) -> Response:
        """Получить список доступных особенностей магазинов для фильтрации."""
        url = f"{self.CATALOG_URL}/shop/features"
        return self._parent._request("GET", url)


class GeolocationSelection:
    """Сервис для выбора точек доставки и магазинов."""
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def shop_point(self, shop_id: int) -> Response:
        """Выбрать магазин. Изменяет содержимое каталога.
        
        Args:
            shop_id: ID магазина для установки как точки самовывоза
        """
        url = f"{self.CATALOG_URL}/delivery/mode/pickup/{shop_id}"
        return self._parent._request("PUT", url)

    def delivery_point(self, position: abstraction.Geoposition) -> Response:
        """Установить точку доставки курьером.
        
        Args:
            position: Координаты точки доставки
        """
        url = f"{self.CATALOG_URL}/delivery/mode/courier"
        body = {
            "apartment": None,
            "location": {
                "coordinates": [position.longitude, position.latitude],
                "type": "Point",
            },
        }
        return self._parent._request("POST", url, json_body=body)

    def delivery_info(self, position: abstraction.Geoposition) -> Response:
        """Получить информацию о доставке для указанных координат.
        
        Args:
            position: Координаты для получения информации о доставке
        """
        url = f"{self.CATALOG_URL}/delivery/info?lat={position.latitude}&lng={position.longitude}"
        return self._parent._request("GET", url)
