"""PyTest, do some socket tests."""

from http import HTTPStatus
from socketserver import TCPServer

from flask.testing import FlaskClient

stop_thread = False


def test_input(sleepless: any, mock_server: TCPServer, client: FlaskClient):
    """Use a socket sender to work as a client."""
    response = client.post("/input/D_GBA_START")
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.post("/input/D_GBA_START", headers={"client-id": "TEST1"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/input/U_GBA_START", headers={"client-id": "TEST2"})
    assert response.status_code == HTTPStatus.OK

    response = client.post("/input/INVALID", headers={"client-id": "TEST3"})
    assert response.status_code == HTTPStatus.OK
    assert response.data == b"INVALID KEYPRESS, DROPPING"


def test_get_status(sleepless: any, mock_server: TCPServer, client: FlaskClient):
    """Use a socket sender to work as a client."""
    response = client.get("/GetStatus")
    assert response.status_code == HTTPStatus.OK
