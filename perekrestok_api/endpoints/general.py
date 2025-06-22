from .. import abstraction as ABSTRACT

class ClassGeneral:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    def download_image(self, url: str):
        return self._parent._request("GET", url)

    def qualifier(self, selections: list[ABSTRACT.QualifierFeatureKey] | None = None):
        """При None вернет ответы по всем ключам."""
        url = f"{self.CATALOG_URL}/qualifier"
        if selections is None:
            selections = ABSTRACT.QualifierFeatureKey.get_all()
        return self._parent._request("POST", url, json_body={"keys": selections})

    def feedback_form(self):
        url = f"{self.CATALOG_URL}/feedback/form"
        return self._parent._request("GET", url)

    def delivery_switcher(self):
        url = f"{self.CATALOG_URL}/delivery/switcher"
        return self._parent._request("GET", url)

    def current_user(self):
        url = f"{self.CATALOG_URL}/user/current"
        return self._parent._request("GET", url)