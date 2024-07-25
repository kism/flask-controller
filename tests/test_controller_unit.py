"""Unit test the controller module."""

import random
import string
import threading
import time
import logging

import pytest

from flaskcontroller import controller


def test_colour_player_id():
    """TEST: The colour ID generator runs without issue."""
    random_strings = []
    for _ in range(1000):
        length = random.randint(0, 10)
        random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        random_strings.append(random_string)

    for my_string in random_string:
        controller.colour_player_id(my_string)


def stop_run_thread(seconds=1.5):
    """Stop infinite loop."""
    time.sleep(seconds)
    controller._run_thread = False


@pytest.fixture()
def socket_os_error(monkeypatch):
    """Patched function TKTKTKTKTK."""
    import socket

    def socket_fail(*args, **kwargs) -> None:  # noqa: ANN002, ANN003, throw away args
        """TKTKTKTKT."""
        raise OSError

    monkeypatch.setattr(socket, "socket", socket_fail)


def test_os_error(socket_os_error, caplog):
    """TKTKKTKTKTK."""
    controller._run_thread = True

    thread = threading.Thread(target=stop_run_thread)
    thread.start()

    controller.socket_sender({})

    thread.join()

    with caplog.at_level(logging.CRITICAL):
        assert "OSError when trying to create socket" in caplog.text


class MockSocket:
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, traceback):
        pass

    def setsockopt(self):
        pass

    def connect(self, *args, **kwargs):  # noqa: ANN002, ANN003, throw away args
        pass


@pytest.fixture()
def socket_connection_refused_error(monkeypatch):
    """Patched function TKTKTKTKTK."""
    import socket

    ms = MockSocket()

    def fake_socket(*args, **kwargs) -> MockSocket:  # noqa: ANN002, ANN003, throw away args
        return ms

    def socket_fail(*args, **kwargs) -> None:  # noqa: ANN002, ANN003, throw away args
        """TKTKTKTKT."""
        raise ConnectionRefusedError

    print(ms)

    monkeypatch.setattr(socket, "socket", fake_socket)
    # monkeypatch.setattr("socket.socket", "setsockopt", fake_socket)


def test_connection_refused_error(socket_connection_refused_error, caplog):
    """TKTKKTKTKTK."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        assert sock is not None
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    assert "YOU DID IT" == "WAHOOOOOO"
    # end testing
    controller._run_thread = True

    thread = threading.Thread(target=stop_run_thread)
    thread.start()

    controller.socket_sender({})

    thread.join()

    with caplog.at_level(logging.CRITICAL):
        assert "OSError when trying to create socket" in caplog.text
