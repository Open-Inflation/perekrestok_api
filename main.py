from perekrestok_api import PerekrestokAPI, ABSTRACT
import tqdm
from pprint import pprint
import asyncio


async def main():
    async with PerekrestokAPI(headless=False, timeout=10.0) as Api:

        feed_filter = ABSTRACT.CatalogFeedFilter()
        feed_filter.PROMO_LISTING = 2
#        feed_filter.CATEGORY_ID = 1558

        # Запрашиваем товары из текущей категории
        catalog_handler = await Api.Catalog.feed(filter=feed_filter)
        pprint(Api.session)
        print("Catalog Feed:", catalog_handler)
        await asyncio.sleep(5)

        return




        # Получение дерева категорий каталога
        tree_handler = await Api.Catalog.tree()
        if isinstance(tree_handler, HandlerSearchFailed):
            for resp in tree_handler.rejected_responses:
                print(f"{resp.status} | {len(resp.request_headers)} | {len(resp.response_headers)}")
                pprint(resp.request_headers)
            return
        
        tree = tree_handler.response

        # Список для хранения всех обработанных товаров
        products = []

        # Прогресс-бар для отображения процесса обработки
        tq = tqdm.tqdm(tree["content"]["items"], desc='Обработано категорий')

        # Рекурсивная функция для обработки категорий и их подкатегорий
        async def process_sub(tree_items, depth=0):
            # Используем прогресс-бар только на верхнем уровне вложенности
            current_level = tq if depth == 0 else tree_items

            for category_group in current_level:
                category = category_group["category"]

                # Формирование фильтра для запроса каталога
                feed_filter = ABSTRACT.CatalogFeedFilter()
                feed_filter.CATEGORY_ID = category["id"]

                # Запрашиваем товары из текущей категории
                catalog_handler = await Api.Catalog.feed(filter=feed_filter)
                print("Catalog Feed:", catalog_handler.status)
                if isinstance(catalog_handler, HandlerSearchFailed):
                    for resp in catalog_handler.rejected_responses:
                        print(f"{resp.status} | {len(resp.request_headers)} | {len(resp.response_headers)}")
                        pprint(resp.request_headers)
                        print()
                #pprint(catalog_handler.request_headers)
                #pprint(catalog_handler.response_headers)

                catalog = catalog_handler.response

                pprint(catalog)

                page = 1

                # Цикл обработки всех страниц товаров в категории
                while page > 0 and len(catalog["content"]["items"]) > 0:
                    for product in catalog["content"]["items"]:
                        # Сохраняем название и ID товара
                        products.append(f'{product["title"]} ({product["id"]})')
                        tq.desc = f'Обработано карточек: {len(products)}'

                    # Переход к следующей странице или завершение обработки
                    if catalog['content']['paginator']['nextPageExists']:
                        page += 1
                        catalog_handler = await Api.Catalog.feed(filter=feed_filter, page=page)
                        print(f"Catalog Feed Page {page}:", catalog_handler.status)
                        catalog = catalog_handler.response
                    else:
                        page = -1

                # Рекурсивно обрабатываем подкатегории
                for child in category_group.get("children", []):
                    await process_sub([child], depth + 1)

        Api.BROWSER._logger.setLevel("DEBUG")
        # Запуск обработки дерева категорий
        await process_sub(tree["content"]["items"])

        # Вывод итоговой статистики
        print(f'Общее количество встреченных карточек: {len(products)}')
        print(f'Уникальных товаров: {len(set(products))}')
        print(f'Среднее количество повторений карточки: {round(len(products) / len(set(products)), 2)}')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())