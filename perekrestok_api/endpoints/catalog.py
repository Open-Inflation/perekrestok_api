from .. import abstraction as ABSTRACT


class ClassCatalog:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def promo_listings_by_id(self, ids: list[int]):
        url = f"{self.CATALOG_URL}/catalog/promo/listings/by-id?{'&'.join([f'ids[]={id}' for id in ids])}"
        return self._parent._request("GET", url)

    def feed(
        self,
        filter: ABSTRACT.CatalogFeedFilter,
        sort: ABSTRACT.CatalogFeedSort = ABSTRACT.CatalogFeedSort.Popularity.ASC,
        page: int = 1,
        limit: int = 100,
        with_best_reviews_only: bool = False,
    ):
        url = f"{self.CATALOG_URL}/catalog/product/feed"
        body = {
            "filter": filter.as_dict(),
            "page": page,
            "perPage": limit,
            "withBestProductReviews": with_best_reviews_only,
        }
        body.update(sort)
        return self._parent._request("POST", url, json_body=body)

    def product(self, product_id: int | str):
        if isinstance(product_id, int) or isinstance(product_id, str):
            if not isinstance(product_id, str) or not product_id.startswith("plu"):
                product_id = f"plu{product_id}"
        else:
            raise TypeError("ID товара должен быть int или str.")
        if not str(product_id).removeprefix("plu").isdigit():
            raise ValueError("ID товара должен быть int или str структуры pluXXX.")
        url = f"{self.CATALOG_URL}/catalog/product/{product_id}"
        return self._parent._request("GET", url)

    def form(
        self,
        filter: ABSTRACT.CatalogFeedFilter,
        disable_bubble_up: bool = False,
        sort_by_alpha: bool = True,
    ):
        url = f"{self.CATALOG_URL}/catalog/search/form"
        body = {
            "filter": filter.as_dict(),
            "disableBubbleUp": disable_bubble_up,
            "sortByAlpha": sort_by_alpha,
        }
        return self._parent._request("POST", url, json_body=body)

    def tree(self):
        url = f"{self.CATALOG_URL}/catalog/tree"
        return self._parent._request("POST", url)
