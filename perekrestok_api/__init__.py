"""
Неофициальная библиотека для работы с API сети магазинов Перекрёсток.

Библиотека позволяет взаимодействовать с каталогом товаров, системой геолокации,
рекламными материалами и общими сервисами Перекрёстка.
"""
# filepath: /home/miskler/Документы/GitHub/perekrestok_api/perekrestok_api/__init__.py
from .manager import PerekrestokAPI

__version__ = "0.1.7"
__all__ = ["PerekrestokAPI"]
