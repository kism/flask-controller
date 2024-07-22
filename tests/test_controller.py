"""PyTest, Tests the controller module in full."""

import logging
import os
import socket
import threading
import time
from http import HTTPStatus

import pytest
from flask.testing import FlaskClient

import flaskcontroller


class TCPServer:
    """Object TCPServer to be used as a test socket server."""

    def __init__(self):
        """Init the socket."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __enter__(self):
        """Implement 'with x as y:."""
        self._sock.bind(("127.0.0.1", 5001))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Deconstruct the object."""
        self._sock.close()

    def listen_for_traffic(self):
        """Loop for socket listener."""
        import logging

        logger = logging.getLogger(__name__)
        while True:
            try:
                self._sock.listen(5)
                connection, address = self._sock.accept()
                message = connection.recv(2)
                msg = f"Address: {address}, Message: {message}"
                logger.info(msg)
            except OSError:
                pass


@pytest.fixture()
def dummy_tcp_server():
    """Dummy TCP Server for pretending to be an emulator."""
    tcp_server = TCPServer()
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


def test_get_status_sock_connected_false(caplog: pytest.LogCaptureFixture, client: FlaskClient):
    """Test the hello API endpoint. This one uses the fixture in conftest.py."""
    with caplog.at_level(logging.WARNING):
        response = client.get("/GetStatus")
        # TEST: The default /hello/ response
        assert response.json["sock_connected"] is False


def test_socket_sender(dummy_tcp_server, tmp_path, caplog: pytest.LogCaptureFixture):
    """Test the controller socket sender."""
    # Since this is the one time that we run the socket sender, I test startup without config too.
    # TEST: File is created when no config is provided.
    with caplog.at_level(logging.WARNING):
        app = flaskcontroller.create_app(test_config=None, instance_path=tmp_path)

        assert "No configuration file found, creating at default location:" in caplog.text
        assert os.path.exists(os.path.join(tmp_path, "config.toml"))

    test_client = app.test_client()

    # TEST: Input endpoints.
    response = test_client.post("/input/D_GBA_START")
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = test_client.post("/input/D_GBA_START", headers={"client-id": "TEST"})
    assert response.status_code == HTTPStatus.OK

    response = test_client.post("/input/U_GBA_START", headers={"client-id": "TEST"})
    assert response.status_code == HTTPStatus.OK

    response = test_client.post("/input/INVALID", headers={"client-id": "TEST"})
    assert response.status_code == HTTPStatus.OK
    assert response.data == b"INVALID KEYPRESS, DROPPING"

    response = test_client.post("/input/D_GBA_START")
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # TEST: GetStatus endpoint
    response = test_client.get("/GetStatus")
    assert response.status_code == HTTPStatus.OK
    assert response.json["sock_connected"] is True

    # Cleanup, I don't like the sleeps but alas
    flaskcontroller.controller._run_thread = False

    caplog.clear()
    caplog.set_level(logging.INFO)

    # Since socket_sender takes a bit to shutdown, we use this to check when it exits.
    retries = 500
    i = 0
    while i < retries and "PyTest stopped socket_sender" not in caplog.text:
        time.sleep(0.1)
        i += 1

    assert "PyTest stopped socket_sender" in caplog.text
