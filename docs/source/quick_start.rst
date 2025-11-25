Quick Start
===========

.. code-block:: console

    pip install perekrestok_api

.. code-block:: python
    
    from perekrestok_api import PerekrestokAPI
    from perekrestok_api import abstraction
    import asyncio


    async def main():
        async with PerekrestokAPI() as Api:
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
            filter.PROMO_LISTING = 27
            products = await Api.Catalog.feed(filter=filter)
            prod = products.json()

            # Выводим первый товар
            print(f'Первый товар: {prod["content"]["items"][0]["title"]} ({prod["content"]["items"][0]["id"]})')

    # Запуск асинхронной функции main
    if __name__ == "__main__":
        asyncio.run(main())

.. code-block:: console

    > Текущий город сессии Москва (81)
    > Список категорий: 31
    > Категория: Встречаем Новый год (1692)
    > Первый товар: Икра Камчатское Море горбуши зернистая солёная, 320г (487063)


Для более подробной информации смотрите референсы :class:`~perekrestok_api.endpoints.catalog.ClassCatalog`, :class:`~perekrestok_api.endpoints.geolocation.ClassGeolocation`, :class:`~perekrestok_api.endpoints.general.ClassGeneral`, :class:`~perekrestok_api.endpoints.advertising.ClassAdvertising` документации.
