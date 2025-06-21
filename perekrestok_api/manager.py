"""core.py — ядро клиента «Перекрёсток»
=====================================
Только логика сессии/авторизации и универсальный `_request()`,
который теперь **возвращает исключительно тело ответа** (dict | list | str | bytes)
— без обёрток и вспомогательных структур.
"""
from __future__ import annotations

import asyncio
import json
import urllib.parse
from typing import Any, Dict

import hrequests

from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation

__all__ = [
    "PerekrestokAPI",
]

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
CATALOG_VERSION = "1.4.1.0"
MAIN_SITE_URL = "https://www.perekrestok.ru"
CATALOG_URL = f"{MAIN_SITE_URL}/api/customer/{CATALOG_VERSION}"

# ---------------------------------------------------------------------------
# Главный клиент
# ---------------------------------------------------------------------------
class PerekrestokAPI:
    def __init__(
        self,
        *,
        access_token: str | None = None,
        timeout: float = 10.0,
        browser: str = "firefox",
        headless: bool = True,
        **browser_opts,
    ) -> None:
        self._timeout = timeout
        self._browser = browser
        self._headless = headless
        self._browser_opts = browser_opts

        # TLS‑сеанс c JA3 нужного браузера
        self.session = hrequests.Session(browser, timeout=timeout)

        self.access_token = access_token

        # Энд‑поинты
        self.Geolocation = ClassGeolocation(self, CATALOG_URL)
        self.Catalog = ClassCatalog(self, CATALOG_URL)
        self.Advertising = ClassAdvertising(self, CATALOG_URL)
        self.General = ClassGeneral(self, CATALOG_URL)

    async def __aenter__(self):
        await self._warmup()
        return self

    async def __aexit__(self, *exc):
        self.close()

    def close(self):
        self.session.close()

    # property setget access_token
    @property
    def access_token(self) -> str | None:
        """Токен доступа, который будет использоваться в запросах."""
        token = self.session.headers.get("Auth", None)
        if token:
            if not token.startswith("Bearer "):
                raise ValueError("Access token must start with 'Bearer '.")
            token = token.removeprefix("Bearer ")
        return token
    @access_token.setter
    def access_token(self, token: str | None) -> None:
        """Установить токен доступа для использования в запросах."""
        if token is not None and not isinstance(token, str):
            raise TypeError("Access token must be a string or None.")

        if token is None:
            self.session.headers.pop("Auth", None)
        else:
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "Auth": f"Bearer {token}"
            })

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    async def _warmup(self) -> None:
        def _sync() -> None:
            with hrequests.BrowserSession(
                session=self.session,
                browser=self._browser,
                headless=self._headless,
                **self._browser_opts,
            ) as page:
                page.goto(MAIN_SITE_URL)
                page.awaitSelector("#app", timeout=self._timeout)

            if "session" not in self.session.cookies:
                raise RuntimeError("Cookie 'session' not found after warmup.")

            raw = urllib.parse.unquote(self.session.cookies["session"])
            clean = json.loads(raw.removeprefix("j:"))
            self.access_token = clean['accessToken']

        if self.access_token is None:
            await asyncio.to_thread(_sync)

    async def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> dict | list | str | bytes:
        def _sync_request():
            resp = self.session.request(method.upper(), url, json=json_body, timeout=self._timeout)
            return resp

        resp = await asyncio.to_thread(_sync_request)

        # best‑effort decode
        try:
            return resp.json()
        except ValueError:
            try:
                return resp.text
            except Exception:  # noqa: BLE001 – fallback
                return resp.content
