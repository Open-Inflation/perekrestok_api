from __future__ import annotations

import imghdr

import pytest
from conftest import make_test


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
def test_general_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))


# Отдельный тест на бинарную загрузку (PNG)
def test_download_image(api):
    image_url = (
        "https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/"
        "files/ae/2a/4f39b2a249768b268ed9f325c155.png"
    )
    resp = api.General.download_image(image_url)
    assert resp.headers["Content-Type"].startswith("image/")
    fmt = imghdr.what(None, resp.raw)
    assert fmt in ("png", "jpeg", "webp")
