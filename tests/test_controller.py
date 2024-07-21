"""PyTest, Tests the hello API endpoint."""

import socket
import threading
from http import HTTPStatus
from socketserver import TCPServer

import pytest
from flask.testing import FlaskClient

from flaskcontroller import create_app


class TCPServer:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __enter__(self):
        self._sock.bind(("127.0.0.1", 5001))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._sock.close()

    def listen_for_traffic(self):
        while True:
            self._sock.listen(5)
            connection, address = self._sock.accept()
            message = connection.recv(2048)
            # response = "Received"
            # connection.send(response.encode())
            # connection.close()


@pytest.fixture(autouse=True)
def dummy_tcp_server():
    tcp_server = TCPServer()
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


@pytest.fixture()
def client_with_socket(tmp_path, get_test_config: dict) -> any:
    """This fixture uses the default config within the flask app."""
    return create_app(test_config=get_test_config("testing_run_socket.toml"), instance_path=tmp_path)


# def test_get_status_sock_connected_false(client: FlaskClient):
#     """Test the hello API endpoint. This one uses the fixture in conftest.py."""
#     response = client.get("/GetStatus")
#     # TEST: The default /hello/ response
#     assert response.json["sock_connected"] is False


def test_get_status_sock_connected_true(tmp_path, get_test_config, caplog: pytest.LogCaptureFixture):
    """TKKTKTKKTKTKTKTKKTKTKTKTKTK."""
    import logging

    from flaskcontroller import controller

    def _do_inputs(test_client):
        import time

        time.sleep(1)
        test_client.post("/input/D_GBA_START", headers={"client_id": "TESTEST"})
        time.sleep(1)
        test_client.post("/input/U_GBA_START", headers={"client_id": "TESTEST"})

        response = test_client.post("/input/D_GBA_START")
        assert response.status_code == HTTPStatus.BAD_REQUEST


        controller._run_thread = False

    test_config = get_test_config("testing_run_socket.toml")
    # _, test_config["app"]["socket_port"] = mock_server.server_address
    test_config["app"]["socket_port"] = 5001

    with caplog.at_level(logging.DEBUG):
        app = create_app(test_config=test_config,instance_path=tmp_path)
        thread = threading.Thread(target=_do_inputs,args=(app.test_client(),))
        thread.daemon = True
        thread.start()
        # controller.socket_sender(test_config)

    thread.join()
    assert thread.exit
    assert "Connected to socketzz" in caplog.text


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
