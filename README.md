<div align="center">

# Perekrestok API (not official)

[![Tests](https://github.com/Open-Inflation/perekrestok_api/actions/workflows/tests.yml/badge.svg)](https://github.com/Open-Inflation/perekrestok_api/actions/workflows/tests.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/perekrestok_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/perekrestok_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/perekrestok_api?label=PyPi%20downloads)](https://pypi.org/project/perekrestok-api/)
[![License](https://img.shields.io/github/license/Open-Inflation/perekrestok_api)](https://github.com/Open-Inflation/perekrestok_api/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)

Perekrestok (Перекрёсток) - https://www.perekrestok.ru/

**[⭐ Star us on GitHub](https://github.com/Open-Inflation/perekrestok_api)** | **[📚 Read the Docs](https://open-inflation.github.io/perekrestok_api/quick_start)** | **[🐛 Report Bug](https://github.com/Open-Inflation/perekrestok_api/issues)**

### Принцип работы

</div>

> Библиотека полностью повторяет сетевую работу обычного пользователя на сайте.

<div align="center">

# Usage

</div>

```py
from perekrestok_api import PerekrestokAPI
from perekrestok_api import abstraction


def main():
    with PerekrestokAPI() as Api:
        geopos_handler = Api.Geolocation.current()
        geopos = geopos_handler.json()
        print(f'Текущий город сессии {geopos["content"]["city"]["name"]} ({geopos["content"]["city"]["id"]})')
    
        # Получаем список категорий
        categories = Api.Catalog.tree()
        cat = categories.json()
        print(f'Список категорий: {len(cat["content"]["items"])}')

        # Выводим первую категорию
        print(f'Категория: {cat["content"]["items"][0]["category"]["title"]} ({cat["content"]["items"][0]["category"]["id"]})')
        # Получаем список товаров
        filter = abstraction.CatalogFeedFilter()
        filter.CATEGORY_ID = cat["content"]["items"][0]["category"]["id"]
        products = Api.Catalog.feed(filter=filter)
        prod = products.json()

        # Выводим первый товар
        print(f'Первый товар: {prod["content"]["items"][0]["title"]} ({prod["content"]["items"][0]["id"]})')

if __name__ == "__main__":
    main()
```
```bash
> Текущий город сессии Москва (81)
> Список категорий: 31
> Категория: Летний сезон (1585)
> Первый товар: Пиво Василеостровское Тройной пшеничный эль нефильтрованное 6.9%, 750мл (66750)
```

Для более подробной информации смотрите референсы [документации](https://open-inflation.github.io/perekrestok_api/quick_start).

---

<div align="center">

### Report

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/perekrestok_api/issues)!

</div>
