from . import abstraction as ABSTRACT

CATALOG_VERSION = "1.4.1.0"
CATALOG_URL = f"https://www.perekrestok.ru/api/customer/{CATALOG_VERSION}"



async def geo_city_current():
    url = f"{CATALOG_URL}/geo/city/current"

async def qualifier(): # POST
    url = f"{CATALOG_URL}/qualifier"

async def feedback_form():
    url = f"{CATALOG_URL}/feedback/form"

async def shop_points():
    url = f"{CATALOG_URL}/shop/points"

async def current_user():
    url = f"{CATALOG_URL}/user/current"

async def delivery_switcher():
    url = f"{CATALOG_URL}/delivery/switcher"

async def catalog_promo_listings_by_id(ids: list[int]):
    url = f"{CATALOG_URL}/catalog/promo/listings/by-id{'&'.join([f'ids[]={id}' for id in ids])}"

async def catalog_product_feed(
        filter: ABSTRACT.CatalogFeedFilter, 
        sort: ABSTRACT.CatalogFeedSort,
        page: int = 1, 
        limit: int = 100,
        best_product_reviews_only: bool = False
    ): # POST
    url = f"{CATALOG_URL}/catalog/product/feed"
    body = {
        "filter": filter.as_dict(),
        "page": page,
        "perPage": limit,
        "withBestProductReviews": best_product_reviews_only
    }.update(sort)

async def catalog_search_form(): # POST # TODO
    ...

async def booklet(city: int = 81):
    url = f"{CATALOG_URL}/booklet?city={city}"

async def banner(places: list[ABSTRACT.BannerPlace]):
    url = f"{CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"
