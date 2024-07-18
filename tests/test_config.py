"""Test launching the app and config."""

import logging
import os

import pytest

from flaskcontroller import create_app


def test_config_valid(get_test_config: dict):
    """Test passing config to app."""
    # TEST: Assert that the config dictionary can set config attributes successfully.
    assert not create_app(
        get_test_config("testing_false_valid")
    ).testing, "Flask testing config item not being set correctly."
    assert create_app(
        get_test_config("testing_true_valid")
    ).testing, "Flask testing config item not being set correctly."


def test_config_file_creation(tmp_path, get_test_config: dict, caplog: pytest.LogCaptureFixture):
    """Tests relating to config file."""
    # # TEST: that file is created when no config is provided.
    caplog.set_level(logging.WARNING)
    create_app(test_config=None, instance_path=tmp_path)
    assert "No configuration file found, creating at default location:" in caplog.text
    caplog.clear()

    # TEST: that file is not created when config is provided.
    caplog.set_level(logging.WARNING)
    create_app(test_config=get_test_config("testing_true_valid"), instance_path=tmp_path)
    assert "No configuration file found, creating at default location:" not in caplog.text


def test_config_file_loading(tmp_path, caplog: pytest.LogCaptureFixture):
    """Tests relating to config file."""
    with open(os.path.join(pytest.TEST_CONFIGS_LOCATION, "testing_true_valid.toml")) as f:
        config_contents = f.read()

    tmp_f = tmp_path / "config.toml"

    tmp_f.write_text(config_contents)

    # TEST: that file is created when no config is provided.
    caplog.set_level(logging.INFO)
    create_app(test_config=None, instance_path=tmp_path)
    assert "Using this path as it's the first one that was found" in caplog.text
    caplog.clear()
