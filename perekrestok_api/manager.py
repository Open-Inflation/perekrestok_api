from __future__ import annotations

import asyncio
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from camoufox.async_api import AsyncCamoufox
from human_requests import HumanBrowser, HumanContext, HumanPage
from human_requests.abstraction import FetchResponse, HttpMethod, Proxy
from human_requests.network_analyzer.anomaly_sniffer import (
    HeaderAnomalySniffer,
    WaitHeader,
    WaitSource,
)
from playwright.async_api import Error as PWError
from playwright.async_api import TimeoutError as PWTimeoutError

from .api_base import ApiParent, api_child_field
from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation


def _pick_https_proxy() -> str | None:
    """Возвращает прокси из HTTPS_PROXY/https_proxy (если заданы)."""
    return os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")


@dataclass
class PerekrestokAPI(ApiParent):
    """
    Клиент Перекрестка.
    """

    timeout_ms: float = 20000.0
    """Время ожидания ответа от сервера в миллисекундах."""
    headless: bool = True
    """Запускать браузер в headless режиме?"""
    proxy: str | dict | None = field(default_factory=_pick_https_proxy)
    """Прокси-сервер для всех запросов (если нужен). По умолчанию берет из окружения (если есть).
    Принимает как формат Playwright, так и строчный формат."""
    browser_opts: dict[str, Any] = field(default_factory=dict)
    """Дополнительные опции браузера.

    Документация: https://camoufox.com/python/installation/
    """
    CATALOG_VERSION = "1.4.1.0"
    MAIN_SITE_URL = "https://www.perekrestok.ru"
    CATALOG_URL = f"{MAIN_SITE_URL}/api/customer/{CATALOG_VERSION}"

    # будет создана в __post_init__
    session: HumanBrowser = field(init=False, repr=False)
    """Внутренняя сессия браузера для выполнения HTTP-запросов."""
    # будет создано в warmup
    ctx: HumanContext = field(init=False, repr=False)
    """Внутренний контекст сессии браузера"""
    page: HumanPage = field(init=False, repr=False)
    """Внутренний страница сессии браузера"""

    unstandard_headers: dict[str, str] = field(init=False, repr=False)
    """Список нестандартных заголовков пойманных при инициализации"""

    Geolocation: ClassGeolocation = api_child_field(ClassGeolocation)
    """API для работы с геолокацией."""
    Catalog: ClassCatalog = api_child_field(ClassCatalog)
    """API для работы с каталогом товаров."""
    Advertising: ClassAdvertising = api_child_field(ClassAdvertising)
    """API для работы с рекламой."""
    General: ClassGeneral = api_child_field(ClassGeneral)
    """API для работы с общими функциями."""

    async def __aenter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        await self._warmup()
        return self

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения человекоподобности."""
        br = await AsyncCamoufox(
            headless=self.headless,
            proxy=Proxy(self.proxy).as_dict(),
            humanize=True,
            geoip=True,
            **self.browser_opts,
        ).start()

        self.session = HumanBrowser.replace(br)
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()

        sniffer = HeaderAnomalySniffer(
            include_subresources=True,  # или False, если интересны только документы
            url_filter=lambda u: u.startswith(self.CATALOG_URL),
        )
        await sniffer.start(self.ctx)

        await self.page.goto(self.MAIN_SITE_URL, wait_until="networkidle")

        async def _click_robot_if_present() -> None:
            try:
                await self.page.locator('label[for="is-robot"].captcha-label').click(
                    timeout=self.timeout_ms,
                )
            except (PWTimeoutError, PWError):
                # captcha опциональна: ошибки клика не должны останавливать warmup
                return

        app_ready = asyncio.create_task(
            self.page.wait_for_selector("#app", timeout=self.timeout_ms)
        )
        captcha_click = asyncio.create_task(_click_robot_if_present())

        done, _pending = await asyncio.wait(
            {app_ready, captcha_click},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if app_ready in done and not captcha_click.done():
            captcha_click.cancel()
            await asyncio.gather(captcha_click, return_exceptions=True)

        await app_ready

        if "session" not in list(map(lambda d: d["name"], await self.page.cookies())):
            raise RuntimeError("Cookie 'session' not found after warmup.")

        await sniffer.wait(
            tasks=[
                WaitHeader(
                    source=WaitSource.REQUEST,
                    headers=["Auth"],
                )
            ],
            timeout_ms=self.timeout_ms,
        )

        result_sniffer = await sniffer.complete()
        # Результат: {заголовок: [уникальные значения]}
        result = defaultdict(set)

        # Проходим по всем URL в 'request'
        for _url, headers in result_sniffer["request"].items():
            for header, values in headers.items():
                result[header].update(values)  # добавляем значения, set уберёт дубли

        # Преобразуем set обратно в list
        self.unstandard_headers = {k: list(v)[0] for k, v in result.items()}

    async def __aexit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        await self.close()

    async def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        await self.session.close()

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        add_unstandard_headers: bool = True,
        credentials: bool = True,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю сессию.

        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp: FetchResponse = await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            credentials="include" if credentials else "omit",
            timeout_ms=self.timeout_ms,
            referrer=self.MAIN_SITE_URL,
            headers={"Accept": "application/json, text/plain, */*"}
            | (self.unstandard_headers if add_unstandard_headers else {}),
        )

        return resp
