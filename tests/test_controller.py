"""PyTest, Tests the hello API endpoint."""

from flask.testing import FlaskClient


def test_hello(client: FlaskClient):
    """Test the hello API endpoint. This one uses the fixture in conftest.py."""
    response = client.get("/GetStatus")
    # TEST: The default /hello/ response
    assert response.json["sock_connected"] is False
