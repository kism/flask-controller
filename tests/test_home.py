"""Tests the home page and static files."""

from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_home(client: FlaskClient) -> None:
    """TEST: The home page renders."""
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.content_type == "text/html; charset=utf-8"
    assert b"<!doctype html>" in response.data


def test_static_js_exists(client: FlaskClient) -> None:
    """TEST: The javascript that the home page loads is served."""
    assert client.get("/static/flaskcontroller.js").status_code == HTTPStatus.OK
