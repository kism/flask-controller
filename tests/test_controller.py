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
        import logging

        logger = logging.getLogger(__name__)
        while True:
            try:
                self._sock.listen(5)
                connection, address = self._sock.accept()
                message = connection.recv(2)
            except OSError:
                pass


@pytest.fixture()
def dummy_tcp_server():
    tcp_server = TCPServer()
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


# def test_get_status_sock_connected_false(client: FlaskClient):
#     """Test the hello API endpoint. This one uses the fixture in conftest.py."""
#     response = client.get("/GetStatus")
#     # TEST: The default /hello/ response
#     assert response.json["sock_connected"] is False


def test_get_status_sock_connected_true(dummy_tcp_server, tmp_path, get_test_config, caplog: pytest.LogCaptureFixture):
    """TKKTKTKKTKTKTKTKKTKTKTKTKTK."""
    import logging

    from flaskcontroller import controller

    test_config = get_test_config("testing_run_socket.toml")
    test_config["app"]["socket_port"] = 5001

    with caplog.at_level(logging.DEBUG):
        app = create_app(test_config=test_config, instance_path=tmp_path)

        test_client = app.test_client()

        response = test_client.post("/input/D_GBA_START")
        assert response.status_code == HTTPStatus.BAD_REQUEST

        response = test_client.post("/input/D_GBA_START", headers={"client-id": "TEST1"})
        assert response.status_code == HTTPStatus.OK

        response = test_client.post("/input/U_GBA_START", headers={"client-id": "TEST2"})
        assert response.status_code == HTTPStatus.OK

        response = test_client.post("/input/INVALID", headers={"client-id": "TEST3"})
        assert response.status_code == HTTPStatus.OK
        assert response.data == b"INVALID KEYPRESS, DROPPING"

        response = test_client.post("/input/D_GBA_START")
        assert response.status_code == HTTPStatus.BAD_REQUEST

        response = test_client.get("/GetStatus")
        assert response.status_code == HTTPStatus.OK

    controller._run_thread = False
    assert "Connected to socket" in caplog.text

    dummy_tcp_server.__exit__(Exception, False, False)
    # assert "PyTest stopped socket_sender" in caplog.text
