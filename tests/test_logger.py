"""Logger tests."""

import logging
from typing import TYPE_CHECKING

import pytest

from flaskcontroller.utils.logger import setup_logger

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.fixture
def logger() -> Generator[logging.Logger]:
    """Logger to use in unit tests, including cleanup since it will persist."""
    logger = logging.getLogger("TEST_LOGGER")
    assert len(logger.handlers) == 0

    yield logger

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)


def test_console_handler(logger: logging.Logger) -> None:
    """TEST: A console handler is added, and only ever one."""
    setup_logger(in_logger=logger)
    assert len(logger.handlers) == 1

    setup_logger(in_logger=logger)
    assert len(logger.handlers) == 1


def test_file_handler(logger: logging.Logger, tmp_path: Path) -> None:
    """TEST: A file handler is added alongside the console handler, and only ever one."""
    setup_logger(log_path=tmp_path / "test.log", in_logger=logger)
    assert len(logger.handlers) == 2

    setup_logger(log_path=tmp_path / "test.log", in_logger=logger)
    assert len(logger.handlers) == 2


def test_log_to_dir(logger: logging.Logger, tmp_path: Path) -> None:
    """TEST: Correct exception when you try log to a directory."""
    with pytest.raises(IsADirectoryError):
        setup_logger(log_path=tmp_path, in_logger=logger)


def test_log_no_permission(logger: logging.Logger, tmp_path: Path, mocker: MockerFixture) -> None:
    """TEST: Correct exception when you can't write to the log file."""
    # ponytail: mocked, real chmod 000 doesn't raise when the tests run as root
    mocker.patch("flaskcontroller.utils.logger.RotatingFileHandler", side_effect=PermissionError)
    with pytest.raises(PermissionError):
        setup_logger(log_path=tmp_path / "test.log", in_logger=logger)


@pytest.mark.parametrize(
    ("log_level_in", "log_level_expected"),
    [(50, 50), ("INFO", 20), ("warning", 30), ("INVALID", 20)],
)
def test_set_log_level(log_level_in: str | int, log_level_expected: int, logger: logging.Logger) -> None:
    """TEST: Log levels, including the invalid level fallback."""
    setup_logger(log_level=log_level_in, in_logger=logger)
    assert logger.getEffectiveLevel() == log_level_expected
