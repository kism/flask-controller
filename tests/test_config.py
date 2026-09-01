"""Tests config loading and writing."""

import json
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from webcontroller.config import CONFIG_FILE_NAME, Config

if TYPE_CHECKING:
    from pathlib import Path


def test_load_missing_config(tmp_path: Path) -> None:
    """TEST: A missing config file results in defaults, written out to the instance directory."""
    config = Config.load(tmp_path)
    assert config.app.socket_port == 5001

    config_path = tmp_path / CONFIG_FILE_NAME
    assert config_path.is_file()
    assert json.loads(config_path.read_text())["app"]["socket_port"] == 5001


def test_load_existing_config(tmp_path: Path) -> None:
    """TEST: An existing config file is loaded, missing fields are filled in and written back."""
    config_path = tmp_path / CONFIG_FILE_NAME
    config_path.write_text('{"app": {"socket_port": 9999}}')

    config = Config.load(tmp_path)
    assert config.app.socket_port == 9999
    assert json.loads(config_path.read_text())["logging"]["level"] == "INFO"


def test_invalid_tick_rate(tmp_path: Path) -> None:
    """TEST: A tick rate of zero fails validation, it would be a divide by zero later."""
    (tmp_path / CONFIG_FILE_NAME).write_text('{"app": {"tick_rate": 0}}')

    with pytest.raises(ValidationError, match="tick_rate must be greater than zero"):
        Config.load(tmp_path)
