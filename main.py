from perekrestok_api import PerekrestokAPI
from perekrestok_api import abstraction
import asyncio
from pprint import pprint


async def main():
    async with PerekrestokAPI() as Api:
        pprint(Api.unstandard_headers)
        geopos_handler = await Api.Geolocation.current()
        geopos = geopos_handler.json()
        print(f'Текущий город сессии {geopos["content"]["city"]["name"]} ({geopos["content"]["city"]["id"]})')
    
        # Получаем список категорий
        categories = await Api.Catalog.tree()
        cat = categories.json()
        print(f'Список категорий: {len(cat["content"]["items"])}')

        # Выводим первую категорию
        print(f'Категория: {cat["content"]["items"][0]["category"]["title"]} ({cat["content"]["items"][0]["category"]["id"]})')
        # Получаем список товаров
        filter = abstraction.CatalogFeedFilter()
        filter.CATEGORY_ID = cat["content"]["items"][0]["category"]["id"]
        products = await Api.Catalog.feed(filter=filter)
        prod = products.json()

        # Выводим первый товар
        print(f'Первый товар: {prod["content"]["items"][0]["title"]} ({prod["content"]["items"][0]["id"]})')

# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())
