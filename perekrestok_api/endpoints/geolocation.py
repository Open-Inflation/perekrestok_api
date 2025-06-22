from .. import abstraction as ABSTRACT


class ClassGeolocation:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self._selection = GeolocationSelection(parent=self._parent, CATALOG_URL=CATALOG_URL)
        self._shop_service = ShopService(parent=self._parent, CATALOG_URL=CATALOG_URL)
        self.CATALOG_URL = CATALOG_URL

    def current(self):
        url = f"{self.CATALOG_URL}/geo/city/current"
        return self._parent._request("GET", url)

    def delivery_address(self):
        url = f"{self.CATALOG_URL}/delivery/address"
        return self._parent._request("GET", url)

    def address_from_position(self, position: ABSTRACT.Geoposition):
        url = f"{self.CATALOG_URL}/geocoder/reverse?lat={position.latitude}&lng={position.longitude}"
        return self._parent._request("GET", url)

    def suggests(self, search: str):
        url = f"{self.CATALOG_URL}/geocoder/suggests?search={search}"
        return self._parent._request("GET", url)

    def search(self, search: str, limit: int = 40):
        url = f"{self.CATALOG_URL}/geo/city?search={search}&limit={limit}"
        return self._parent._request("GET", url)

    @property
    def Selection(self):
        return self._selection

    @property
    def Shop(self):
        return self._shop_service

class ShopService:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def all(self):
        url = f"{self.CATALOG_URL}/shop/points"
        return self._parent._request("GET", url)

    def info(self, shop_id: int):
        url = f"{self.CATALOG_URL}/shop/{shop_id}"
        return self._parent._request("GET", url)

    def on_map(
        self,
        position: ABSTRACT.Geoposition | None = None,
        page: int = 1,
        limit: int = 10,
        city_id: int | None = None,
        sort: ABSTRACT.GeolocationPointSort = ABSTRACT.GeolocationPointSort.Distance.ASC,
        features: list[int] | None = None,
    ):
        url = f"{self.CATALOG_URL}/shop?orderBy={sort['orderBy']}&orderDirection={sort['orderDirection']}&page={page}&perPage={limit}"
        if city_id:
            url += f"&cityId={city_id}"
        if isinstance(position, ABSTRACT.Geoposition):
            url += f"&lat={position.latitude}&lng={position.longitude}"
        if features:
            url += "&" + "&".join([f"features[]={f}" for f in features])
        return self._parent._request("GET", url)

    def features(self):
        url = f"{self.CATALOG_URL}/shop/features"
        return self._parent._request("GET", url)


class GeolocationSelection:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def shop_point(self, shop_id: int):
        url = f"{self.CATALOG_URL}/delivery/mode/pickup/{shop_id}"
        return self._parent._request("PUT", url)

    def delivery_point(self, position: ABSTRACT.Geoposition):
        url = f"{self.CATALOG_URL}/delivery/mode/courier"
        body = {
            "apartment": None,
            "location": {
                "coordinates": [position.longitude, position.latitude],
                "type": "Point",
            },
        }
        return self._parent._request("POST", url, json_body=body)

    def delivery_info(self, position: ABSTRACT.Geoposition):
        url = f"{self.CATALOG_URL}/delivery/info?lat={position.latitude}&lng={position.longitude}"
        return self._parent._request("GET", url)
