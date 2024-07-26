"""Unit test the controller module."""

import logging
import random
import socket
import string
import threading
import time

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


def test_os_error(monkeypatch, caplog):
    """Test OSError on Socket creation."""

    def socket_fail(*args, **kwargs) -> None:
        """Immediate socket failure with OSError."""
        raise OSError

    monkeypatch.setattr(socket, "socket", socket_fail)

    controller._run_thread = True

    thread = threading.Thread(target=stop_run_thread)
    thread.start()

    controller.socket_sender({})

    thread.join()

    with caplog.at_level(logging.CRITICAL):
        assert "OSError when trying to create socket" in caplog.text


class MockSocketConnectionRefusedError:
    """Mock Object."""

    def __init__(self, *args, **kwargs):
        """Mocked."""

    def __enter__(self):
        """Mocked."""
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """Mocked."""

    def setsockopt(self, *args, **kwargs):
        """Mocked."""

    def connect(self, *args, **kwargs):
        """Mocked Exception."""
        raise ConnectionRefusedError


def test_connection_refused_error(tmp_path, get_test_config, mocker, caplog):
    """Test connection refused error."""
    mocker.patch.object(socket, "socket", MockSocketConnectionRefusedError)

    import flaskcontroller

    test_config = get_test_config("testing_true_valid.toml")

    flaskcontroller.create_app(test_config=test_config, instance_path=tmp_path)

    controller._run_thread = True

    thread = threading.Thread(target=stop_run_thread)
    thread.start()

    controller.socket_sender({"app": {"socket_address": "127.0.0.1", "socket_port": "9999", "tick_rate": 120}})

    thread.join()

    with caplog.at_level(logging.ERROR):
        assert "Socket connection refused" in caplog.text

    with caplog.at_level(logging.INFO):
        assert "Trying again" in caplog.text


class MockSocketBrokenPipeError:
    """Mock Object."""

    def __init__(self, *args, **kwargs):
        """Mocked."""

    def __enter__(self):
        """Mocked."""
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """Mocked."""

    def setsockopt(self, *args, **kwargs):
        """Mocked."""

    def connect(self, *args, **kwargs):
        """Mocked."""

    def sendall(self, *args, **kwargs):
        """Mocked Error."""
        raise BrokenPipeError


def test_connection_broken_pipe_error(tmp_path, get_test_config, mocker, caplog):
    """Test Broken Pipe Error exception."""
    mocker.patch.object(socket, "socket", MockSocketBrokenPipeError)

    import flaskcontroller

    test_config = get_test_config("testing_true_valid.toml")

    flaskcontroller.create_app(test_config=test_config, instance_path=tmp_path)

    controller.input_queue.append(1)
    controller._run_thread = True

    thread = threading.Thread(target=stop_run_thread)
    thread.start()

    controller.socket_sender({"app": {"socket_address": "127.0.0.1", "socket_port": "9999", "tick_rate": 120}})

    thread.join()

    with caplog.at_level(logging.ERROR):
        assert "Disconnected from socket, cringe" in caplog.text

    with caplog.at_level(logging.INFO):
        assert "Attempt: 2/∞" in caplog.text
