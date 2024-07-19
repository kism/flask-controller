"""PyTest, Tests the hello API endpoint."""

from http import HTTPStatus
from socketserver import TCPServer

import pytest
from flask.testing import FlaskClient

from flaskcontroller import create_app


@pytest.fixture()
def client_with_socket(tmp_path, get_test_config: dict) -> any:
    """This fixture uses the default config within the flask app."""
    return create_app(test_config=get_test_config("testing_run_socket.toml"), instance_path=tmp_path)


def test_get_status_sock_connected_false(client: FlaskClient):
    """Test the hello API endpoint. This one uses the fixture in conftest.py."""
    response = client.get("/GetStatus")
    # TEST: The default /hello/ response
    assert response.json["sock_connected"] is False


def test_get_status_sock_connected_true(tmp_path, get_test_config, mock_server: TCPServer, caplog: pytest.LogCaptureFixture):
    """TKKTKTKKTKTKTKTKKTKTKTKTKTK."""
    import logging

    from flaskcontroller import controller

    test_config = get_test_config("testing_run_socket.toml")
    _, test_config["app"]["socket_port"] = mock_server.server_address


    with caplog.at_level(logging.DEBUG):
        controller.socket_sender(test_config)



# def test_input(sleepless: any, mock_server: TCPServer, app_with_socket: FlaskClient):
#     """Use a socket sender to work as a client."""
#     response = client_with_socket.client().post("/input/D_GBA_START")
#     assert response.status_code == HTTPStatus.BAD_REQUEST

#     response = client_with_socket.client().post("/input/D_GBA_START", headers={"client-id": "TEST1"})
#     assert response.status_code == HTTPStatus.OK

#     response = client_with_socket.client().post("/input/U_GBA_START", headers={"client-id": "TEST2"})
#     assert response.status_code == HTTPStatus.OK

#     response = client_with_socket.client().post("/input/INVALID", headers={"client-id": "TEST3"})
#     assert response.status_code == HTTPStatus.OK
#     assert response.data == b"INVALID KEYPRESS, DROPPING"


# def test_get_status(sleepless: any, mock_server: TCPServer, app_with_socket: FlaskClient):
#     """Use a socket sender to work as a client."""
#     response = client_with_socket.client().get("/GetStatus")
#     assert response.status_code == HTTPStatus.OK
