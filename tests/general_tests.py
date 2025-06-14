# test_general.py
import pytest
from io import BytesIO
from typed_schema_shot import SchemaShot
from perekrestok_api import PerekrestokAPI


@pytest.mark.asyncio
async def test_qualifier(schemashot: SchemaShot):
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.General.qualifier()
        schemashot.assert_match(handler.response, "qualifier")


@pytest.mark.asyncio
async def test_feedback_form(schemashot: SchemaShot):
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.General.feedback_form()
        schemashot.assert_match(handler.response, "feedback_form")


@pytest.mark.asyncio
async def test_delivery_switcher(schemashot: SchemaShot):
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.General.delivery_switcher()
        schemashot.assert_match(handler.response, "delivery_switcher")


@pytest.mark.asyncio
async def test_current_user(schemashot: SchemaShot):
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        handler = await api.General.current_user()
        schemashot.assert_match(handler.response, "current_user")


@pytest.mark.asyncio
async def test_download_image(schemashot: SchemaShot):
    async with PerekrestokAPI(debug=False, timeout=10.0) as api:
        image_url = (
            "https://cdn-img.perekrestok.ru/i/400x400-fit/xdelivery/files/"
            "ae/2a/4f39b2a249768b268ed9f325c155.png"
        )
        image_data = await api.General.download_image(image_url)

        assert isinstance(image_data, BytesIO)
        assert len(image_data.getvalue()) > 0

        image_data.seek(0)
        assert image_data.read(8) == b'\x89PNG\r\n\x1a\n'
