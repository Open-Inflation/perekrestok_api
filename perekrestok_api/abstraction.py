
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

    NEW_GENERAL_CHAT = "new_general_chat"
    """Новый общий чат"""

    PHOTO_REVIEW = "photo_review"
    """Фотоотзыв о продукте"""

    PREORDER_X5D = "preorder_x5d"
    """Предпросмотр заказа X5D"""

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

        DISCOUNT_DETAILS = "discount_details_epl"
        """Детали скидки EPL"""

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
    
    @staticmethod
    def get_all():
        """Собирает все значения из QualifierFeatureKey"""
        keys = []
        
        # Основные ключи
        for attr_name, attr_value in QualifierFeatureKey.__dict__.items():
            if not attr_name.startswith('_') and isinstance(attr_value, str):
                keys.append(attr_value)
        
        # Ключи из вложенных классов
        for attr_name, attr_value in QualifierFeatureKey.__dict__.items():
            if isinstance(attr_value, type):  # Это класс
                for nested_attr_name, nested_attr_value in attr_value.__dict__.items():
                    if not nested_attr_name.startswith('_') and isinstance(nested_attr_value, str):
                        keys.append(nested_attr_value)
        
        return keys


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
        Является в большей степени внутренним методом.
        
        `hidden_key` - это имя фильтра воспринимаемое сервером Перекрестка. Внутри бибилиотеки создана обёртка с другими неймами для удобства и ясности.
        """
        filters = {}
        for key, filter_obj in self.__class__.__dict__.items():
            if isinstance(filter_obj, self._Filter):
                dict_key = filter_obj.hidden_key if use_hidden_key else key
                parts = dict_key.split("/")
                current = filters

                # Исключаем невалидные значения
                if filter_obj.value == -1 or (isinstance(filter_obj, self._FeaturesFilter) and not filter_obj.value):
                    continue

                # Обработка FEATURES
                if isinstance(filter_obj, self._FeaturesFilter):
                    current[dict_key] = filter_obj.to_list()
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

    class _FeaturesFilter(_Filter):
        """Класс для работы с фильтром FEATURES."""

        def __init__(self, default_value, property_type: type, hidden_key: str):
            super().__init__(default_value, property_type, hidden_key)
            if not isinstance(default_value, dict):
                raise TypeError("Значение FEATURES должно быть словарём.")

        def add(self, key: str, value: str):
            """Добавляет новую особенность в FEATURES."""
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("Ожидаются строки для ключа и значения.")
            self._value.setdefault(key, [])
            if value not in self._value[key]:
                self._value[key].append(value)

        def remove(self, key: str, value: str):
            """Удаляет особенность из FEATURES."""
            if key in self._value and value in self._value[key]:
                self._value[key].remove(value)
                if not self._value[key]:  # Удаляем ключ, если список пуст
                    del self._value[key]

        def to_list(self):
            """Конвертирует структуру FEATURES в список словарей."""
            return [{"key": k, "value": v} for k, values in self._value.items() for v in values]

        def __repr__(self):
            return str(self._value)
        
        def __set__(self, instance, value):
            raise AttributeError(f"{self.hidden_key} не может быть изменён напрямую. Используйте add() и remove()")

    # Определение фильтров с использованием дескриптора
    CATEGORY_ID = _Filter(-1, int, "category") # 1389 - "Фрукты, овощи: акции и скидки"
    """ID категорий бывают 2 видов - главные и дочерние. По сути они имеют одинаковый и равный статус для системы."""

    PROMO_LISTING = _Filter(-1, int, "promoListing")
    """Работает как фильтр (при != -1), т.е. отбраковываются товары не учавствующие в акции.
    Описание акций можно получить по `.Catalog.promo_listings_by_id(спиок_id_акций)`.
    От куда брать доступные id остаётся загадкой. Можно просто перебрать id от 1 до N (пару сотен, думаю, достаточно).
    """

    FROM_PEREKRESTOK = _Filter(False, bool, "privateLabel")
    """Исключает товары не являющиеся внутренним брендом сети (только СТМ)."""

    ONLY_DISCOUNT = _Filter(False, bool, "onlyDiscount")
    """Исключает товары без скидки (по регулярной цене)."""

    ONLY_WITH_REVIEWS = _Filter(False, bool, "onlyWithProductReviews")
    """Исключает товары без отзывов (требуется уточнение: без отзывов или без оценок)."""

    LOWEST_PRICE = _Filter(-1, int, "priceRange/from")
    """Фильтр исключающий цену в копейках где `<N`. По умолчанию -1 (отсутствует).
    Диапазон цен для текущего поиска можно получить с помощью `.Catalog.form()['content']['priceFrom']` (цена передаётся в копейках так же в копейках).

    Рекумендую использовать только в паре с `HIGHEST_PRICE`, т.к. я не знаю как сервер воспримет посылку только одного поля.
    Т.е. используйте `self.set_price_range(lowest, highest)`"""

    HIGHEST_PRICE = _Filter(-1, int, "priceRange/to")
    """Фильтр исключающий цену в копейках где `>N`. По умолчанию -1 (отсутствует).
    Диапазон цен для текущего поиска можно получить с помощью `.Catalog.form()['content']['priceTo']` (цена передаётся в копейках так же в копейках).

    Рекумендую использовать только в паре с `LOWEST_PRICE`, т.к. я не знаю как сервер воспримет посылку только одного поля.
    Т.е. используйте `self.set_price_range(lowest, highest)`"""

    FEATURES = _FeaturesFilter({}, dict, "features")
    """Фильтр для \"особенностей\" продукта. Таких как: страна изготовитель, тип продукта, бренд и тп.
    
    Для получения доступных особенностей обратитесь к `.Catalog.form()['content']['searchFeatures']`.
    Ключ для `.add()`/`.remove()` Вы можете найти в `key` на первом уровне массива словарей, 
    внутри такого словаря так же будет `enumList` содержащий массив словарей с доступными значениями фильтра в `value`.
    """

class _SortOption:
    def __init__(self, order_by: str):
        self.ASC = {"orderBy": order_by, "orderDirection": "asc"}
        self.DESC = {"orderBy": order_by, "orderDirection": "desc"}

class CatalogFeedSort():
    Price = _SortOption("price")
    Popularity = _SortOption("popularity")
    Discount = _SortOption("discount")
    Rating = _SortOption("rating")
    Recommended = _SortOption("popularity_without_manual")

class GeolocationPointSort:
    Distance = _SortOption("distance")

class Geoposition:
    """
    Если передавать координаты через кортеж/массив, то они идут как [долгота, широта] (стандарт для ответов от Перекрестка).
    При передаче как отдельных неименованных параметров, то они идут как [широта, долгота] (стандарт для мира).
    """

    def __init__(self, *args, longitude=None, latitude=None, coordinates=None):
        if coordinates and isinstance(coordinates, (list, tuple)) and len(coordinates) == 2:
            self.longitude, self.latitude = coordinates
        elif latitude is not None and longitude is not None:
            self.latitude = latitude
            self.longitude = longitude
        elif len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) == 2:
            self.longitude, self.latitude = args[0]
        elif len(args) == 2 and all(isinstance(arg, float) for arg in args):
            self.latitude, self.longitude = args
        else:
            raise ValueError("Provide either two floats or a list/tuple with two elements [longitude, latitude], or named parameters.")
