from __future__ import annotations

import pytest
from conftest import make_test
from PIL import Image


# Все независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        pytest.param(lambda api: api.General.qualifier, id="qualifier"),
        pytest.param(lambda api: api.General.feedback_form, id="feedback_form"),
        pytest.param(lambda api: api.General.delivery_switcher, id="delivery_switcher"),
        pytest.param(lambda api: api.General.current_user, id="current_user"),
    ],
)
async def test_general_matrix(api, schemashot, factory):
    await make_test(schemashot, factory(api))


# Отдельный тест на бинарную загрузку (PNG)
async def test_download_image(api):
    image_url = (
        "https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/"
        "files/ae/2a/4f39b2a249768b268ed9f325c155.png"
    )
    resp = await api.General.download_image(image_url)

    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")
