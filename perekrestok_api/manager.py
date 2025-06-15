import asyncio
import json
import urllib.parse
from dataclasses import dataclass
from time import monotonic

import hrequests

from . import abstraction as ABSTRACT

CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"{MAIN_SITE_URL}/api/customer/{CATALOG_VERSION}"


def _remove_csrf_prefixes(text: str) -> str:
    text = text.lstrip()
    json_start_chars = ['{', '[']
    for i, char in enumerate(text):
        if char in json_start_chars:
            stack = []
            in_string = False
            escaped = False
            for j in range(i, len(text)):
                current = text[j]
                if escaped:
                    escaped = False
                    continue
                if current == '\\':
                    escaped = True
                    continue
                if current == '"' and not escaped:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if current in ['{', '[']:
                    stack.append(current)
                elif current in ['}', ']']:
                    if not stack:
                        break
                    expected = '{' if current == '}' else '['
                    if stack[-1] == expected:
                        stack.pop()
                        if not stack:
                            candidate = text[i:j+1]
                            try:
                                json.loads(candidate)
                                return candidate
                            except json.JSONDecodeError:
                                break
                    else:
                        break
    return text


@dataclass
class Response:
    status: int
    request_headers: dict
    response_headers: dict
    response: object | None = None
    duration: float = 0.0
    url: str | None = None


class PerekrestokAPI:
    def __init__(self, debug: bool = False, **kwargs):
        self.timeout: float = kwargs.get("timeout", 10.0)
        self.session = hrequests.TLSSession(browser="chrome", timeout=self.timeout)
        self.headers: dict[str, str] = {}
        self._geolocation = self._ClassGeolocation(self)
        self._catalog = self._ClassCatalog(self)
        self._general = self._ClassGeneral(self)
        self._advertising = self._ClassAdvertising(self)

    async def __aenter__(self):
        await asyncio.to_thread(self._init_session)
        return self

    def _init_session(self):
        resp = self.session.request("GET", MAIN_SITE_URL, timeout=self.timeout)
        if "session" in self.session.cookies:
            raw = urllib.parse.unquote(self.session.cookies["session"])
            clean_json = json.loads(_remove_csrf_prefixes(raw))
            self.headers["Auth"] = f"Bearer {clean_json['accessToken']}"

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.session.close()

    async def _request(self, method: str, url: str, *, json_body=None) -> Response:
        req_headers = self.headers.copy()

        def do_request():
            start = monotonic()
            resp = self.session.request(method, url, json=json_body, headers=req_headers, timeout=self.timeout)
            duration = monotonic() - start
            return resp, duration

        resp, duration = await asyncio.to_thread(do_request)
        try:
            body = resp.json()
        except Exception:
            body = resp.raw
        return Response(
            status=resp.status_code,
            request_headers=req_headers,
            response_headers=dict(resp.headers),
            response=body,
            duration=duration,
            url=resp.url,
        )

    class _ClassGeolocation:
        def __init__(self, parent: "PerekrestokAPI"):
            self._parent = parent
            self._selection = self._GeolocationSelection(parent=self._parent)
            self._shop_service = self._ShopService(parent=self._parent)

        async def current(self) -> Response:
            url = f"{CATALOG_URL}/geo/city/current"
            return await self._parent._request("GET", url)

        async def delivery_address(self) -> Response:
            url = f"{CATALOG_URL}/delivery/address"
            return await self._parent._request("GET", url)

        async def search(self, search: str, limit: int = 40) -> Response:
            url = f"{CATALOG_URL}/geo/city?search={search}&limit={limit}"
            return await self._parent._request("GET", url)

        class _ShopService:
            def __init__(self, parent: "PerekrestokAPI"):
                self._parent = parent

            async def all(self) -> Response:
                url = f"{CATALOG_URL}/shop/points"
                return await self._parent._request("GET", url)

            async def info(self, shop_id: int) -> Response:
                url = f"{CATALOG_URL}/shop/{shop_id}"
                return await self._parent._request("GET", url)

            async def on_map(
                self,
                position: ABSTRACT.Geoposition | None = None,
                page: int = 1,
                limit: int = 10,
                city_id: int | None = None,
                sort: ABSTRACT.GeologicationPointSort = ABSTRACT.GeologicationPointSort.Distance.ASC,
                features: list[int] | None = None,
            ) -> Response:
                url = f"{CATALOG_URL}/shop?orderBy={sort['orderBy']}&orderDirection={sort['orderDirection']}&page={page}&perPage={limit}"
                if city_id:
                    url += f"&cityId={city_id}"
                if isinstance(position, ABSTRACT.Geoposition):
                    url += f"&lat={position.latitude}&lng={position.longitude}"
                if features:
                    url += "&" + "&".join([f"features[]={f}" for f in features])
                return await self._parent._request("GET", url)

            async def features(self) -> Response:
                url = f"{CATALOG_URL}/shop/features"
                return await self._parent._request("GET", url)

        class _GeolocationSelection:
            def __init__(self, parent: "PerekrestokAPI"):
                self._parent = parent

            async def shop(self, shop_id: int) -> Response:
                url = f"{CATALOG_URL}/delivery/mode/pickup/{shop_id}"
                return await self._parent._request("PUT", url)

            async def delivery_point(self, position: ABSTRACT.Geoposition) -> Response:
                url = f"{CATALOG_URL}/delivery/mode/courier"
                body = {
                    "apartment": None,
                    "location": {
                        "coordinates": [position.longitude, position.latitude],
                        "type": "Point",
                    },
                }
                return await self._parent._request("POST", url, json_body=body)

        @property
        def Selection(self):
            return self._selection

        @property
        def Shop(self):
            return self._shop_service

    class _ClassCatalog:
        def __init__(self, parent: "PerekrestokAPI"):
            self._parent = parent

        async def promo_listings_by_id(self, ids: list[int]) -> Response:
            url = f"{CATALOG_URL}/catalog/promo/listings/by-id{'&'.join([f'ids[]={id}' for id in ids])}"
            return await self._parent._request("GET", url)

        async def feed(
            self,
            filter: ABSTRACT.CatalogFeedFilter,
            sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
            page: int = 1,
            limit: int = 100,
            with_best_reviews_only: bool = False,
        ) -> Response:
            url = f"{CATALOG_URL}/catalog/product/feed"
            body = {
                "filter": filter.as_dict(),
                "page": page,
                "perPage": limit,
                "withBestProductReviews": with_best_reviews_only,
            }
            body.update(sort)
            return await self._parent._request("POST", url, json_body=body)

        async def product(self, product_id: int | str) -> Response:
            if isinstance(product_id, int) or isinstance(product_id, str):
                if not isinstance(product_id, str) or not product_id.startswith("plu"):
                    product_id = f"plu{product_id}"
            else:
                raise TypeError("ID товара должен быть int или str.")
            if not str(product_id).removeprefix("plu").isdigit():
                raise ValueError("ID товара должен быть int или str структуры pluXXX.")
            url = f"{CATALOG_URL}/catalog/product/{product_id}"
            return await self._parent._request("GET", url)

        async def form(
            self,
            filter: ABSTRACT.CatalogFeedFilter,
            disable_bubble_up: bool = False,
            sort_by_alpha: bool = True,
        ) -> Response:
            url = f"{CATALOG_URL}/catalog/search/form"
            body = {
                "filter": filter.as_dict(),
                "disableBubbleUp": disable_bubble_up,
                "sortByAlpha": sort_by_alpha,
            }
            return await self._parent._request("POST", url, json_body=body)

        async def tree(self) -> Response:
            url = f"{CATALOG_URL}/catalog/tree"
            return await self._parent._request("POST", url)

    class _ClassAdvertising:
        def __init__(self, parent: "PerekrestokAPI"):
            self._parent = parent

        async def banner(self, places: list[ABSTRACT.BannerPlace]) -> Response:
            url = f"{CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
            return await self._parent._request("GET", url)

        async def main_slider(self, page: int = 1, limit: int = 10) -> Response:
            url = f"{CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
            return await self._parent._request("GET", url)

        async def booklet(self, city: int = 81) -> Response:
            url = f"{CATALOG_URL}/booklet?city={city}"
            return await self._parent._request("GET", url)

        async def view_booklet(self, booklet_id: int) -> Response:
            url = f"{CATALOG_URL}/booklet/{booklet_id}"
            return await self._parent._request("GET", url)

    class _ClassGeneral:
        def __init__(self, parent: "PerekrestokAPI"):
            self._parent = parent

        async def download_image(self, url: str) -> Response:
            return await self._parent._request("GET", url)

        async def qualifier(self) -> Response:
            url = f"{CATALOG_URL}/qualifier"
            return await self._parent._request("POST", url)

        async def feedback_form(self) -> Response:
            url = f"{CATALOG_URL}/feedback/form"
            return await self._parent._request("GET", url)

        async def delivery_switcher(self) -> Response:
            url = f"{CATALOG_URL}/delivery/switcher"
            return await self._parent._request("GET", url)

        async def current_user(self) -> Response:
            url = f"{CATALOG_URL}/user/current"
            return await self._parent._request("GET", url)

    @property
    def Geolocation(self) -> _ClassGeolocation:
        return self._geolocation

    @property
    def Catalog(self) -> _ClassCatalog:
        return self._catalog

    @property
    def Advertising(self) -> _ClassAdvertising:
        return self._advertising

    @property
    def General(self) -> _ClassGeneral:
        return self._general
