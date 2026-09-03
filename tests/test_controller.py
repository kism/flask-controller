"""Tests the controller routes and the socket sender."""

import re
import threading
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

import pytest
from conftest import wait_for
from fastapi.testclient import TestClient

from webcontroller import create_app
from webcontroller.config import AppConf, Config
from webcontroller.services.controller import Button, Controller, colour_player_id

if TYPE_CHECKING:
    import socket
    from pathlib import Path

    from fastapi import FastAPI

HEADERS = {"client-id": "TEST01"}


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


def test_socket_sender(fake_gba, tmp_path: Path) -> None:
    """TEST: The sender connects, ships queued input as little endian bytes, and stops when asked."""
    config = Config(app=AppConf(socket_port=fake_gba.port, run_socket=True))

    app = create_app(config=config, instance_path=tmp_path)
    controller = app.state.controller

    try:
        assert wait_for(lambda: controller.sock_connected), "Never connected to the fake GBA client"

        with TestClient(app) as client:
            assert press(client, "GBA_L", down=True).status_code == HTTPStatus.NO_CONTENT

        # fake_gba decodes as little endian, so a wrong byte order in the app decodes to the wrong button.
        assert fake_gba.wait_for_states([Button.GBA_L.bit]), f"Got {fake_gba.states}"
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
