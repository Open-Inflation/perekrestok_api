import pytest
from perekrestok_api import PerekrestokAPI
from typing import Any
import time
from hrequests import Response
from json import JSONDecodeError


def is_not_error(response: Any) -> None:
    """Check that response doesn't contain an error."""
    time.sleep(0.1)

    try:
        content = response.json()
    except JSONDecodeError:
        raise ValueError("\n".join([
            "Response is not valid JSON.",
            f"URL: {response.url}",
            f"HTTP Method: {response.request.method}",
            f"Status: {response.status_code}",
            f"Content-Type: {response.headers.get('Content-Type', 'unknown')}",
            response.text[:500]  # Show first 500 characters of the response text
        ]))
    except Exception as e:
        raise e
    
    if isinstance(response, Response) and "error" in content:
        raise AssertionError("\n".join([
            f"API returned error: {content['error']['code']}",
            f"URL: {response.url}",
            f"HTTP Method: {response.request.method}",
            f"Status: {response.status_code}"
        ]))


@pytest.fixture(scope="session")
def api():
    """Single API fixture for all tests."""
    with PerekrestokAPI() as api_instance:
        yield api_instance