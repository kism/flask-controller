"""Test launching the app and config."""

import logging

import pytest

from flaskcontroller import create_app


def test_config_valid(tmp_path, get_test_config):
    """Test that the app can load config and the testing attribute is set."""
    # TEST: Testing attribute set
    app = create_app(get_test_config("testing_true_valid.toml"), instance_path=tmp_path)
    assert app.testing, "Flask testing config item not being set correctly."

    # TEST: Testing attribute not set.
    # The config loaded sets testing to False, do not use this config for any other test.
    app = create_app(get_test_config("testing_false_valid.toml"), instance_path=tmp_path)
    assert not app.testing, "Flask testing config item not being set correctly."


def test_config_file_loading(tmp_path, place_test_config, caplog: pytest.LogCaptureFixture):
    """Test config file loading, use tmp_path."""
    place_test_config("testing_true_valid.toml", tmp_path)

    # TEST: Config file is created when no test_config is provided.
    caplog.set_level(logging.INFO)
    create_app(test_config=None, instance_path=tmp_path)
    assert "Using this path as it's the first one that was found" in caplog.text
