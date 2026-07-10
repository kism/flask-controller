"""Test the logger of the app."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from flaskcontroller import create_app

if TYPE_CHECKING:
    from types import FunctionType

    import pytest


def test_config_invalid_log_level(tmp_path, get_test_config: FunctionType, caplog: pytest.LogCaptureFixture):
    """Test if logging to file works."""
    with caplog.at_level(logging.WARNING):
        create_app(get_test_config("logging_invalid_log_level.toml"), instance_path=tmp_path)

    # TEST: Assert that the invalid logging level message gets logged
    assert "Invalid logging level" in caplog.text
