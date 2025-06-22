from .. import abstraction as ABSTRACT


class ClassAdvertising:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def banner(self, places: list[ABSTRACT.BannerPlace]):
        url = f"{self.CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
        return self._parent._request("GET", url)

    def main_slider(self, page: int = 1, limit: int = 10):
        url = f"{self.CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
        return self._parent._request("GET", url)

    def booklet(self, city: int = 81):
        url = f"{self.CATALOG_URL}/booklet?city={city}"
        return self._parent._request("GET", url)

    def view_booklet(self, booklet_id: int):
        url = f"{self.CATALOG_URL}/booklet/{booklet_id}"
        return self._parent._request("GET", url)
