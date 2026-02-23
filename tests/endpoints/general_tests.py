from __future__ import annotations

from PIL import Image


async def test_download_image(api):
    image_url = (
        "https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/"
        "files/ae/2a/4f39b2a249768b268ed9f325c155.png"
    )
    resp = await api.General.download_image(image_url)

    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")
