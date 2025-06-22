# Perekrestok API (not official)

[![Tests](https://github.com/Open-Inflation/perekrestok_api/actions/workflows/check-tests.yml/badge.svg)](https://github.com/Open-Inflation/perekrestok_api/actions/workflows/check-tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-tested%20daily-brightgreen?logo=pytest&logoColor=white)](https://github.com/Open-Inflation/perekrestok_api/actions/workflows/check-tests.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/perekrestok_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/perekrestok_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/perekrestok_api?label=PyPi%20downloads)](https://pypi.org/project/perekrestok-api/)
[![License](https://img.shields.io/github/license/Open-Inflation/perekrestok_api)](https://github.com/Open-Inflation/perekrestok_api/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)

Perekrestok (Перекрёсток) - https://www.perekrestok.ru/

### Принцип работы

> Библиотека полностью повторяет сетевую работу обычного пользователя на сайте.
Основная логика сетевых запросов заложена в `api.py`, она управляется `PerekrestokAPI()` в `manager.py`.
Существует вспомогательный модуль `abstraction.py` хранящий в себе статичные классы, которых принимаю в аргументах некоторые методы в `PerekrestokAPI()`.



# Usage / Использование
### Базовая структура
```py
import asyncio
from perekrestok_api import PerekrestokAPI, ABSTRACT

async def main():
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Работа с геолокацией в сессии:
*От геолокации и способа получения (доставка/забрать из магазина) зависит выдача каталога!*
```py
async with PerekrestokAPI(
        debug = False, # Включить ли логирование библиотеки
        token_retry_attempts = 3 # Количество попыток авторизации
    ) as Api:
    geopos_handler = await Api.Geolocation.current()
    geopos = geopos_handler.response
    print(f'Текущий город сессии {geopos["content"]["city"]["name"]} ({geopos["content"]["city"]["id"]})')

    # Ищем геолокацию города по названию
    content_handler = await Api.Geolocation.search("нижневартовск")
    content = content_handler.response

    # Ищем магазины в этом городе
    point_in_city_handler = await Api.Geolocation.Shop.on_map(
        # Мы можем выбрать магазины на карте через геопозицию
        position=ABSTRACT.Geoposition(content['content']['items'][0]['location']['coordinates']),
        # Или через ID населенного пункта (особой разницы нет). Эти параметры не противоречат друг другу.
        city_id=content['content']['items'][0]['id'],
        
        # Количество магазинов в ответе
        limit=3,

        # Фильтр особенностей магазина, `4` - это кофепоинт
        # С актуальным списком "особенностей" для магазинов можно ознакомиться в `await Api.Geolocation.Shop.features()`
        features=[4],

        # Сортировка как "самый ближайший"
        sort=ABSTRACT.GeologicationPointSort.Distance.ASC
    )
    point_in_city = point_in_city_handler.response

    # Выбираем первый (по сути центральный, т.к. сортировка по удалению от конкретной точки)
    shop_handler = await Api.Geolocation.Selection.shop(point_in_city['content']['items'][0]['id'])
    shop = shop_handler.response
    print(f'Выбран магазин \"{shop["content"]["shop"]["title"]}\", по адресу {shop["content"]["shop"]["address"]}')

    # Теперь можем проверить, действительно ли сменили геолокацию
    geopos_handler = await Api.Geolocation.current()
    geopos = geopos_handler.response

    print(f'Текущий город сессии {geopos["content"]["city"]["name"]} ({geopos["content"]["city"]["id"]})')
```
```bash
> Текущий город сессии Москва (81)
> Выбран магазин "ТЦ Green Park", по адресу Ханты-Мансийский Автономный округ - Югра, г Нижневартовск, ул Ленина, зд 8
> Текущий город сессии Нижневартовск (73)
```

---

### Взаимодействие с каталогом

```py
async with PerekrestokAPI() as Api:
    # Получение дерева категорий каталога
    tree_handler = await Api.Catalog.tree()
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
            catalog = catalog_handler.response
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
                    catalog = catalog_handler.response
                else:
                    page = -1

            # Рекурсивно обрабатываем подкатегории
            for child in category_group.get("children", []):
                await process_sub([child], depth + 1)

    # Запуск обработки дерева категорий
    await process_sub(tree["content"]["items"])

    # Вывод итоговой статистики
    print(f'Общее количество встреченных карточек: {len(products)}')
    print(f'Уникальных товаров: {len(set(products))}')
    print(f'Среднее количество повторений карточки: {round(len(products) / len(set(products)), 2)}')
```
```bash
> Обработано карточек: 41620: 100%|█████████████████████████| 29/29 [03:56<00:00,  8.15s/it]
> Общее количество встреченных карточек: 41620
> Уникальных товаров: 17630
> Среднее количество повторений карточки: 2.36
```

---

### Загрузка изображений
```py
async with PerekrestokAPI() as Api:
    img = await Api.General.download_image("https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/files/ae/2a/4f39b2a249768b268ed9f325c155.png")

    with open(img.name, "wb") as f:
        f.write(img.read())
```

### Или параллельная загрузка
```py
async with PerekrestokAPI() as Api:
    tasks = [
        Api.General.download_image("https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/files/ae/2a/4f39b2a249768b268ed9f325c155.png"),
        Api.General.download_image("https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/files/ae/2a/4f39b2a249768b268ed9f325c155.png")
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        with open(result.name, "wb") as f:
            f.write(result.read())
```

---

### Report / Обратная связь

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/perekrestok_api/issues)!

Если у вас возникнут проблемы в использовании / пожелания, не стесняйтесь писать на [GitHub проекта](https://github.com/Open-Inflation/perekrestok_api/issues)!
