from . import abstraction as ABSTRACT


CATALOG_VERSION = "1.4.1.0"
CATALOG_URL = f"https://www.perekrestok.ru/api/customer/{CATALOG_VERSION}"



async def geo_city_current():
    url = f"{CATALOG_URL}/geo/city/current"

async def search_city(search: str, limit: int = 40):
    url = f"{CATALOG_URL}/geo/city?search={search}&limit={limit}"

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
    """
    Возвращает сам список товаров по фильтрам и сортировке
    """

    url = f"{CATALOG_URL}/catalog/product/feed"
    body = {
        "filter": filter.as_dict(),
        "page": page,
        "perPage": limit,
        "withBestProductReviews": best_product_reviews_only
    }.update(sort)

async def catalog_search_form(
        disable_bubble_up: bool = False,
        sort_by_alpha: bool = True,
): # POST
    """
    Возвращает структуру доступной для поиска информации (доступные фильтры для текущей сессии в текущем каталоге)
    """
    
    url = f"{CATALOG_URL}/catalog/search/form"
    body = {
        "disableBubbleUp": disable_bubble_up,
        "sortByAlpha": sort_by_alpha
    }

async def catalog_tree(): # POST
    """
    Возвращает полное дерево каталога (сессио-независимое)
    """

    url = f"{CATALOG_URL}/catalog/tree"

async def booklet(city: int = 81):
    """
    Спец. категории по типу "суперцена"
    """

    url = f"{CATALOG_URL}/booklet?city={city}"

async def view_booklet(booklet_id: int):
    """
    Просмотр спец. категории. Обычно возвращает JSON структуру где так же есть ссылка на PDF файл с акцией.
    """
    
    url = f"{CATALOG_URL}/booklet/{booklet_id}"

async def banner(places: list[ABSTRACT.BannerPlace]):
    url = f"{CATALOG_URL}/banner?{'&'.join([f'places[]={place}' for place in places])}"

async def catalog_main_slider(page: int = 1, limit: int = 10):
    """
    Рекламные объявления на категории брендов
    """

    url = f"{CATALOG_URL}/catalog/product-brand/main-slider?perPage={limit}&page={page}"
