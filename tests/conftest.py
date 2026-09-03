"""The conftest.py file serves as a means of providing fixtures for an entire directory.

Fixtures defined in a conftest.py can be used by any test in that package without needing to import them.

Tests should always use the tmp_path fixture as an instance_path so they don't pollute each other.
"""

import socket
import threading
import time
from typing import TYPE_CHECKING

import pytest
import uvicorn
from fastapi.testclient import TestClient

from webcontroller import create_app
from webcontroller.config import AppConf, Config

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from fastapi import FastAPI


def wait_for(predicate: Callable[[], bool], timeout: float = 5.0) -> bool:
    """Poll a predicate until it's true or we give up."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def config() -> Config:
    """Default config, with the socket sender thread disabled."""
    return Config(app=AppConf(run_socket=False))


@pytest.fixture
def app(tmp_path: Path, config: Config) -> FastAPI:
    """App with the default config, in a tmp_path instance directory."""
    return create_app(config=config, instance_path=tmp_path)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient]:
    """Test client for the app."""
    with TestClient(app) as test_client:
        yield test_client


class FakeGba:
    """The emulator end of the TCP socket: listens, and remembers every button state the app sends."""

    def __init__(self) -> None:
        self._server = socket.create_server(("127.0.0.1", 0))
        self.port: int = self._server.getsockname()[1]
        self.states: list[int] = []  # Button bitmasks, in the order they arrived.

    def serve(self) -> None:
        """Accept one emulator connection at a time, decoding the two byte states the app sends."""
        while True:
            try:
                connection, _ = self._server.accept()
            except OSError:
                return
            with connection:
                while data := connection.recv(2):
                    self.states.append(int.from_bytes(data, "little"))

    def wait_for_states(self, expected: list[int], timeout: float = 5.0) -> bool:
        """Wait for exactly these states to have arrived."""
        return wait_for(lambda: self.states == expected, timeout)

    def close(self) -> None:
        """Stop listening, which ends serve()."""
        self._server.close()


@pytest.fixture
def fake_gba() -> Generator[FakeGba]:
    """A fake mGBA/Bizhawk lua client, listening on a random port."""
    gba = FakeGba()
    threading.Thread(target=gba.serve, daemon=True).start()

    yield gba

    gba.close()


@pytest.fixture
def live_url(fake_gba: FakeGba, tmp_path: Path) -> Generator[str]:
    """The app, served by uvicorn on a random port, wired to the fake GBA client. For the end to end tests."""
    config = Config(app=AppConf(socket_port=fake_gba.port, run_socket=True))
    app = create_app(config=config, instance_path=tmp_path)

    # Bind ourselves rather than using port 0, so the url is known before the server thread starts.
    sock = socket.create_server(("127.0.0.1", 0))
    server = uvicorn.Server(uvicorn.Config(app, log_config=None))
    threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True).start()

    yield f"http://127.0.0.1:{sock.getsockname()[1]}"

    server.should_exit = True
    app.state.controller.stop()
