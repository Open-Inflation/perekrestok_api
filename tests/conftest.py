# Updated conftest.py
from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

import pytest

from perekrestok_api import PerekrestokAPI


async def is_not_error(response: Any) -> None:
    """
    Базовая проверка успешного ответа:
    - HTTP статус < 400
    - тело корректно JSON-декодится
    - нет ключа 'error' в корне
    """
    await asyncio.sleep(0.5)  # слегка притормаживаем частоту запросов асинхронно

    status = getattr(response, "status_code", 200)
    if status >= 400:
        url = getattr(response, "url", "?")
        txt = getattr(response, "text", "")[:500]
        raise AssertionError(
            f"HTTP {status} at {url.full_url}\n{txt}\n{response.request}"
        )

    try:
        content = response.json()
    except Exception as e:
        url = getattr(response, "url", "?")
        txt = getattr(response, "text", "")[:500]
        raise AssertionError(f"Response is not valid JSON at {url}: {e}\n{txt}")

    if isinstance(content, dict) and "error" in content:
        raise AssertionError(f"API returned error: {content['error']}")


async def make_test(
    schemashot,
    call: Callable[..., Any],
    name: str = "main",
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Универсальный шорткат:
      - вызывает эндпоинт,
      - проверяет отсутствие ошибок,
      - делает снапшот через assert_json_match.

    Аргументы эндпоинта передавайте через kwargs или functools.partial,
    чтобы не перепутать с параметром `name`.
    """
    resp = await call(*args, **kwargs)
    await is_not_error(resp)
    data = resp.json()
    # Новая версия умеет строить имя по callable; добавим подпуть `name`.
    schemashot.assert_json_match(data, (call, name))
    return resp


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Переопределяет фикстуру anyio_backend, чтобы использовать asyncio
    для всей сессии, устраняя ScopeMismatch с фикстурой 'api'.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def api() -> PerekrestokAPI:
    """Сессионный клиент API."""
    async with PerekrestokAPI() as client:
        yield client
