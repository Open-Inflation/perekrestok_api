from __future__ import annotations

import pytest

from perekrestok_api import PerekrestokAPI

pytest_plugins = [
    "tests.endpoints.advertising_tests",
    "tests.endpoints.catalog_tests",
    "tests.endpoints.geolocation_tests",
]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def api() -> PerekrestokAPI:
    async with PerekrestokAPI() as client:
        yield client
