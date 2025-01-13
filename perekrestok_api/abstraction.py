
class BannerPlace:
    """Место показа баннера"""

    MAIN_BANNERS = "main_web_banners"
    """Главные баннеры"""

    BRANDS = "web_brands"
    """Бренды"""

    CATEGORY = "web_category"
    """Категория"""


    class SpecialCategory:
        """Специальная категория"""

        TITLE = "web_spec_category_title"
        """Заголовок специальной категории"""

        LEFT = "web_spec_category_left"
        """Левый баннер специальной категории"""

        RIGHT = "web_spec_category_right"
        """Правый баннер специальной категории"""

class QualifierFeatureKey:
    """Ключи функционала API"""

    VIRTUAL_CARD_BLOCK = "virtual_card_block"
    """Блокировка виртуальной карты"""

    BASKET_DELIVERY_BANNER = "basket_delivery_banner_web"
    """Баннер доставки корзины"""

    STICKERS_AVAILABILITY = "stickers_availability"
    """Доступность стикеров"""

    SPAM_TRAP = "spam_trap"
    """Механизм защиты от спама"""

    AB_EXP = "ab_exp_web"
    """Эксперименты A/B тестирования"""

    PRODUCT_REVIEW_UPLOAD_IMAGE = "product_review_upload_image"
    """Загрузка изображений в отзыве о продукте"""

    PARTNERS = "partners"
    """Список партнёров"""

    CHARITY = "charity"
    """Функционал благотворительности"""

    CARD_ACTIVATION_UNAVAILABLE = "card_activation_unavailable"
    """Недоступность активации карты"""

    LOYALTY_CARD_NOTIFICATION = "loyalty_card_notification"
    """Уведомление о лояльности карты"""

    PURCHASE_HISTORY_NOTIFICATION = "purchase_history_notification"
    """Уведомление о истории покупок"""

    LOYALTY_LEVELS = "loyalty_levels"
    """Уровни лояльности"""

    LOYALTY_ACHIEVEMENT = "loyalty_achievement"
    """Достижения в лояльности"""

    TAG_TREES = "tag_trees"
    """Дерево тегов"""

    PRODUCT_REVIEW = "product_review_web"
    """Отзыв о продукте"""

    CHECKOUT_PROMO = "checkout_promo"
    """Промоакции на этапе оформления заказа"""

    class EPL:
        """Ключи функционала EPL"""

        PARTNERS = "partners_web_epl"
        """Партнёры EPL"""

        BAR_CLUB = "bar_club_web_epl"
        """Бар-клуб EPL"""

        EDINYI_RAZDEL_X5 = "edinyi_razdel_x5_epl"
        """Единый раздел X5 в EPL"""

        ORANGE_BANNER = "orange_banner_epl"
        """Оранжевый баннер EPL"""

        ORANGE_CASHBACK = "orange_cashback_epl"
        """Оранжевый кэшбэк EPL"""

        VIP_DETAILS = "vip_details_epl"
        """Детали VIP EPL"""

        X5_BANNER = "x5_banner_web_epl"
        """Баннер X5 в EPL"""

        PACKET_PROMO = "packet_promo_web_epl"
        """Промо-пакет EPL"""

        VIRTUAL_ORANGE = "virtual_orange_web_epl"
        """Виртуальный оранжевый EPL"""

        BAR_CLUB_FORMS = "bar_club_forms_epl"
        """Формы бар-клуба EPL"""

        FAVORITE_CATEGORY_V2 = "favorite_category_v2_epl"
        """Избранная категория V2 EPL"""

    class Emergency:
        """Экстренные ключи"""

        DISABLE_LOGIN = "emergency_disable_login"
        """Отключение авторизации"""

        DISABLE_CHECKOUT = "emergency_disable_checkout"
        """Отключение оформления заказа"""

class CatalogFeedFilter:
    """Фильтры каталога с параметрами"""

    def set_price_range(self, lowest: float, highest: float):
        """Устанавливает диапазон цен.
        
        Args:
            lowest (float): Минимальная цена.
            highest (float): Максимальная цена.
        """
        if lowest > highest:
            raise ValueError("Минимальная цена не может быть больше максимальной.")
        self.LOWEST_PRICE = lowest
        self.HIGHEST_PRICE = highest

    def as_dict(self, use_hidden_key: bool = True) -> dict:
        """Преобразует фильтры в словарь с учетом вложенности ключей и исключает фильтры с невалидными значениями.
        
        Args:
            use_hidden_key (bool, optional): Использовать ли скрытые ключи. 
                Defaults to True.

        Returns:
            dict: Словарь фильтров.
        """
        filters = {}
        for key, filter_obj in self.__class__.__dict__.items():
            if isinstance(filter_obj, self._Filter):
                dict_key = filter_obj.hidden_key if use_hidden_key else key
                parts = dict_key.split("/")
                current = filters

                # Исключаем невалидные значения
                if filter_obj.value == -1:
                    continue

                # Создаем вложенные словари
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = filter_obj.value

        # Убираем пустые словари, если все ключи в priceRange отсутствуют
        if "priceRange" in filters and not filters["priceRange"]:
            del filters["priceRange"]

        return filters

    class _Filter:
        """Фильтр с параметрами value и hidden_key"""
        
        def __init__(self, default_value, property_type: type, hidden_key: str):
            self._value = default_value
            self._property_type = property_type
            self._hidden_key = hidden_key

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, new_value):
            try:
                self._value = self._property_type(new_value)
            except (ValueError, TypeError):
                raise TypeError(f"Value must be of type {self._property_type.__name__}") from None

        @property
        def hidden_key(self):
            return self._hidden_key

        @property
        def property_type(self):
            return self._property_type

        def __repr__(self):
            return f"{self.hidden_key}: {self.property_type.__name__} = {self.value}"
        
        def __set__(self, instance, value):
            self.value = value

    # Определение фильтров с использованием дескриптора
    CATEGORY_ID = _Filter(1389, int, "category") # 1389 - "Фрукты, овощи: акции и скидки"
    PROMO_LISTING = _Filter(30, int, "promoListing")
    FROM_PEREKRESTOK = _Filter(False, bool, "privateLabel")
    ONLY_DISCOUNT = _Filter(False, bool, "onlyDiscount")
    LOWEST_PRICE = _Filter(-1, float, "priceRange/from")
    HIGHEST_PRICE = _Filter(-1, float, "priceRange/to")


class CatalogFeedSort:
    class _SortOption:
        def __init__(self, order_by: str):
            self.ASC = {"orderBy": order_by, "orderDirection": "asc"}
            self.DESC = {"orderBy": order_by, "orderDirection": "desc"}

    Price = _SortOption("price")
    Popularity = _SortOption("popularity")
    Discount = _SortOption("discount")
    Rating = _SortOption("rating")
    Reccomended = _SortOption("popularity_without_manual")
