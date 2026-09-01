"""Tests the controller routes and the socket sender."""

import re
import socket
import threading
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

import pytest

from flaskcontroller import create_app
from flaskcontroller.config import AppConf, Config
from flaskcontroller.services.controller import Button, Controller, colour_player_id

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from flask.testing import FlaskClient

HEADERS = {"client-id": "TEST01"}


def wait_for(predicate, timeout: float = 5.0) -> bool:
    """Poll a predicate until it's true or we give up."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return False


# --- Routes ----------------------------------------------------------------


def test_get_status(client: FlaskClient) -> None:
    """TEST: GetStatus reports the socket state and counts the pinging client."""
    response = client.get("/GetStatus", headers=HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"sock_connected": False, "players_connected": 1}


def test_input_no_client_id(client: FlaskClient) -> None:
    """TEST: An input without a client id is rejected."""
    response = client.post("/input/D_GBA_START")

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("da_input", ["INVALID", "X_GBA_A", "D_GBA_NOPE", "D_"])
def test_input_invalid(client: FlaskClient, da_input: str) -> None:
    """TEST: An unparseable input is dropped, not an error."""
    response = client.post(f"/input/{da_input}", headers=HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert response.data == b"INVALID KEYPRESS, DROPPING"


def test_input_updates_state(client: FlaskClient, app) -> None:
    """TEST: Down sets the button's bit, up clears it, both get queued."""
    controller = app.extensions["controller"]

    assert client.post("/input/D_GBA_A", headers=HEADERS).status_code == HTTPStatus.OK
    assert controller._state == Button.GBA_A

    assert client.post("/input/D_GBA_START", headers=HEADERS).status_code == HTTPStatus.OK
    assert controller._state == Button.GBA_A | Button.GBA_START

    assert client.post("/input/U_GBA_A", headers=HEADERS).status_code == HTTPStatus.OK
    assert controller._state == Button.GBA_START

    assert [controller._queue.get_nowait() for _ in range(3)] == [
        Button.GBA_A,
        Button.GBA_A | Button.GBA_START,
        Button.GBA_START,
    ]


# --- Controller unit -------------------------------------------------------


def test_client_timeout(config: Config) -> None:
    """TEST: A client that stopped pinging is dropped from the player count."""
    controller = Controller(config.app)

    controller.ping("STALE1")
    controller.clients["STALE1"] -= 10  # Pretend that ping was 10 seconds ago
    controller.ping("FRESH1")

    assert list(controller.clients) == ["FRESH1"]


@pytest.mark.parametrize("player_id", ["", "a", "abc", "abcdef", "abcdefghijk", "   "])
def test_colour_player_id(player_id: str) -> None:
    """TEST: Player ids of any length colourise consistently, keeping the first six characters."""
    coloured = colour_player_id(player_id)

    assert coloured == colour_player_id(player_id)
    assert re.sub(r"\x1b\[[0-9;]*m", "", coloured) == player_id[:6].ljust(6)


def test_no_socket_thread(app) -> None:
    """TEST: run_socket=False means no socket sender thread."""
    assert not any(thread.name == "socket_sender" for thread in threading.enumerate())
    assert app.extensions["controller"].sock_connected is False


# --- Socket sender ---------------------------------------------------------


@pytest.fixture
def dummy_emulator() -> Generator[tuple[int, list[bytes]]]:
    """A TCP server pretending to be mGBA, yields its port and the bytes it received."""
    received: list[bytes] = []
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(1)

    def serve() -> None:
        while True:
            try:
                connection, _ = server.accept()
            except OSError:
                return
            with connection:
                while data := connection.recv(2):
                    received.append(data)

    threading.Thread(target=serve, daemon=True).start()

    yield server.getsockname()[1], received

    server.close()


def test_socket_sender(dummy_emulator, tmp_path: Path) -> None:
    """TEST: The sender connects, ships queued input as little endian bytes, and stops when asked."""
    port, received = dummy_emulator
    config = Config(app=AppConf(socket_port=port, run_socket=True), flask={"TESTING": True})

    app = create_app(config=config, instance_path=tmp_path)
    controller = app.extensions["controller"]

    try:
        assert wait_for(lambda: controller.sock_connected), "Never connected to the dummy emulator"

        client = app.test_client()
        assert client.post("/input/D_GBA_L", headers=HEADERS).status_code == HTTPStatus.OK

        assert wait_for(lambda: received), "Nothing arrived at the dummy emulator"
        assert received[0] == int(Button.GBA_L).to_bytes(2, "little")
    finally:
        controller.stop()

    assert wait_for(lambda: not any(thread.name == "socket_sender" for thread in threading.enumerate())), (
        "Socket sender thread did not stop"
    )


def test_socket_sender_reconnects(tmp_path: Path, caplog) -> None:
    """TEST: A refused connection is logged and retried rather than killing the thread."""
    config = Config(app=AppConf(socket_port=1, run_socket=True), flask={"TESTING": True})

    app = create_app(config=config, instance_path=tmp_path)
    controller = app.extensions["controller"]

    try:
        assert wait_for(lambda: caplog.text.count("Trying again...") >= 2), "Did not retry the connection"
    finally:
        controller.stop()

    assert "Socket connection failed" in caplog.text


def test_send_loop_disconnect(config: Config, caplog) -> None:
    """TEST: A broken pipe mid-send ends the send loop, so the outer loop reconnects."""
    controller = Controller(config.app)
    controller.press(Button.GBA_A, down=True)

    class BrokenSocket:
        def sendall(self, _data: bytes) -> None:
            raise BrokenPipeError

    controller._send_loop(cast("socket.socket", BrokenSocket()))

    assert "Disconnected from socket, cringe" in caplog.text
