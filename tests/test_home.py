"""Tests the home page and static files."""

from http import HTTPStatus
from typing import TYPE_CHECKING

from webcontroller.constants import PROGRAM_NAME_WITH_FULL_VERSION

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_home(client: TestClient) -> None:
    """TEST: The home page renders, with the version on it."""
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"].startswith("text/html")
    assert "<!doctype html>" in response.text
    assert PROGRAM_NAME_WITH_FULL_VERSION in response.text


def test_static_js_exists(client: TestClient) -> None:
    """TEST: The home page's script bundle loads, one entrypoint per template lives in static/."""
    assert client.get("/static/home.js").status_code == HTTPStatus.OK
