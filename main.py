from perekrestok_api import PerekrestokAPI
from perekrestok_api import abstraction
import tqdm
from pprint import pprint
import asyncio


from perekrestok_api import PerekrestokAPI
import tqdm
from pprint import pprint
import time


def main():
    with PerekrestokAPI(headless=False, timeout=10.0) as Api:

        feed_filter = abstraction.CatalogFeedFilter()
        feed_filter.PROMO_LISTING = 2
#        feed_filter.CATEGORY_ID = 1558

        # Запрашиваем товары из текущей категории
        catalog_handler = Api.Catalog.feed(filter=feed_filter)
        pprint(Api.session)
        print("Catalog Feed:", catalog_handler)
        time.sleep(5)

if __name__ == "__main__":
    main()