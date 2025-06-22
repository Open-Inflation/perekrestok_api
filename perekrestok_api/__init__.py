from .manager import PerekrestokAPI
from .abstraction import *

__version__ = "0.1.6.1"
__all__ = ["PerekrestokAPI", "ABSTRACT"]

class ABSTRACT:
    BannerPlace = BannerPlace
    QualifierFeatureKey = QualifierFeatureKey
    CatalogFeedFilter = CatalogFeedFilter
    CatalogFeedSort = CatalogFeedSort
    GeolocationPointSort = GeolocationPointSort
    Geoposition = Geoposition
