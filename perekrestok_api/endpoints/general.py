
class ClassGeneral:
    def __init__(self, parent, CATALOG_URL: str):
        self._parent = parent
        self.CATALOG_URL = CATALOG_URL

    async def download_image(self, url: str):
        return await self._parent._request("GET", url)

    async def qualifier(self):
        url = f"{self.CATALOG_URL}/qualifier"
        return await self._parent._request("POST", url)

    async def feedback_form(self):
        url = f"{self.CATALOG_URL}/feedback/form"
        return await self._parent._request("GET", url)

    async def delivery_switcher(self):
        url = f"{self.CATALOG_URL}/delivery/switcher"
        return await self._parent._request("GET", url)

    async def current_user(self):
        url = f"{self.CATALOG_URL}/user/current"
        return await self._parent._request("GET", url)