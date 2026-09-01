"""Tests the controller routes and the socket sender."""

import re
import socket
import threading
import time
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

import pytest
from fastapi.testclient import TestClient

from webcontroller import create_app
from webcontroller.config import AppConf, Config
from webcontroller.services.controller import Button, Controller, colour_player_id

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from fastapi import FastAPI

HEADERS = {"client-id": "TEST01"}


def wait_for(predicate, timeout: float = 5.0) -> bool:
    """Poll a predicate until it's true or we give up."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return False


def press(client: TestClient, button: str, *, down: bool):
    """POST a button press/release."""
    return client.post("/input", headers=HEADERS, json={"button": button, "down": down})


# --- Routes ----------------------------------------------------------------


def test_get_status(client: TestClient) -> None:
    """TEST: /status reports the socket state and counts the pinging client."""
    response = client.get("/status", headers=HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"sock_connected": False, "players_connected": 1}


def test_status_no_client_id(client: TestClient) -> None:
    """TEST: The client-id header is required."""
    assert client.get("/status").status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_input_no_client_id(client: TestClient) -> None:
    """TEST: An input without a client id is rejected."""
    response = client.post("/input", json={"button": "GBA_START", "down": True})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "body",
    [{"button": "GBA_NOPE", "down": True}, {"button": "GBA_A"}, {"down": True}, {}],
)
def test_input_invalid(client: TestClient, body: dict) -> None:
    """TEST: An unknown button or a missing field is rejected by FastAPI's validation."""
    response = client.post("/input", headers=HEADERS, json=body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_input_updates_state(client: TestClient, app: FastAPI) -> None:
    """TEST: Down sets the button's bit, up clears it, both get queued."""
    controller = app.state.controller

    assert press(client, "GBA_A", down=True).status_code == HTTPStatus.NO_CONTENT
    assert controller._state == Button.GBA_A.bit

    assert press(client, "GBA_START", down=True).status_code == HTTPStatus.NO_CONTENT
    assert controller._state == Button.GBA_A.bit | Button.GBA_START.bit

    assert press(client, "GBA_A", down=False).status_code == HTTPStatus.NO_CONTENT
    assert controller._state == Button.GBA_START.bit

    assert [controller._queue.get_nowait() for _ in range(3)] == [
        Button.GBA_A.bit,
        Button.GBA_A.bit | Button.GBA_START.bit,
        Button.GBA_START.bit,
    ]


# --- Controller unit -------------------------------------------------------


def test_button_bits() -> None:
    """TEST: The bits match mGBA's button codes, the lua scripts depend on these exact values."""
    assert [button.bit for button in Button] == [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]


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


def test_no_socket_thread(app: FastAPI) -> None:
    """TEST: run_socket=False means no socket sender thread."""
    assert not any(thread.name == "socket_sender" for thread in threading.enumerate())
    assert app.state.controller.sock_connected is False


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
    config = Config(app=AppConf(socket_port=port, run_socket=True))

    app = create_app(config=config, instance_path=tmp_path)
    controller = app.state.controller

    try:
        assert wait_for(lambda: controller.sock_connected), "Never connected to the dummy emulator"

        with TestClient(app) as client:
            assert press(client, "GBA_L", down=True).status_code == HTTPStatus.NO_CONTENT

        assert wait_for(lambda: received), "Nothing arrived at the dummy emulator"
        assert received[0] == Button.GBA_L.bit.to_bytes(2, "little")
    finally:
        controller.stop()

    assert wait_for(lambda: not any(thread.name == "socket_sender" for thread in threading.enumerate())), (
        "Socket sender thread did not stop"
    )


def test_socket_sender_reconnects(tmp_path: Path, caplog) -> None:
    """TEST: A refused connection is logged and retried rather than killing the thread."""
    config = Config(app=AppConf(socket_port=1, run_socket=True))

    app = create_app(config=config, instance_path=tmp_path)
    controller = app.state.controller

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
