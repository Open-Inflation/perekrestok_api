from __future__ import annotations

import time
from typing import Any, Callable

import pytest
from perekrestok_api import PerekrestokAPI


def is_not_error(response: Any) -> None:
    """
    Минимальная универсальная проверка успешного ответа:
    - HTTP статус < 400
    - JSON-декодится
    - В корне нет ключа 'error'
    """
    time.sleep(0.05)  # чуть приглушаем частоту запросов

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

    Передавайте аргументы для эндпоинта через kwargs или functools.partial,
    чтобы не пересечься с параметром `name`.
    """
    resp = call(*args, **kwargs)
    is_not_error(resp)
    data = resp.json()
    # Новая версия умеет генерировать имя по callable; также добавим под-имя `name`.
    schemashot.assert_json_match(data, (call, name))
    return resp


@pytest.fixture(scope="session")
def api() -> PerekrestokAPI:
    """Сессионный клиент API."""
    with PerekrestokAPI() as client:
        yield client
