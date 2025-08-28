from __future__ import annotations

import time
from typing import Any, Callable

import pytest
from perekrestok_api import PerekrestokAPI


def is_not_error(response: Any) -> None:
    """
    Базовая проверка успешного ответа:
    - HTTP статус < 400
    - тело корректно JSON-декодится
    - нет ключа 'error' в корне
    """
    time.sleep(0.5)  # слегка притормаживаем частоту запросов

    status = getattr(response, "status_code", 200)
    if status >= 400:
        url = getattr(response, "url", "?")
        txt = getattr(response, "text", "")[:500]
        raise AssertionError(f"HTTP {status} at {url}\n{txt}")

    try:
        content = response.json()
    except Exception as e:
        url = getattr(response, "url", "?")
        txt = getattr(response, "text", "")[:500]
        raise AssertionError(f"Response is not valid JSON at {url}: {e}\n{txt}")

    if isinstance(content, dict) and "error" in content:
        raise AssertionError(f"API returned error: {content['error']}")


def make_test(
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
    resp = call(*args, **kwargs)
    is_not_error(resp)
    data = resp.json()
    # Новая версия умеет строить имя по callable; добавим подпуть `name`.
    schemashot.assert_json_match(data, (call, name))
    return resp


@pytest.fixture(scope="session")
def api() -> PerekrestokAPI:
    """Сессионный клиент API."""
    with PerekrestokAPI() as client:
        yield client
