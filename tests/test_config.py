"""Test launching the app and config."""

import logging
import os

import pytest

from flaskcontroller import create_app


# def test_config_valid(tmp_path, get_test_config):
#     """Test that the app can load config and the testing attribute is set."""
#     # TEST: Testing attribute set
#     app = create_app(get_test_config("testing_true_valid.toml"), instance_path=tmp_path)
#     assert app.testing, "Flask testing config item not being set correctly."

#     # TEST: Testing attribute not set.
#     # The config loaded sets testing to False, do not use this config for any other test.
#     app = create_app(get_test_config("testing_false_valid.toml"), instance_path=tmp_path)
#     assert not app.testing, "Flask testing config item not being set correctly."


# def test_config_file_loading(tmp_path, caplog: pytest.LogCaptureFixture):
#     """Test config file loading, use tmp_path."""
#     with open(os.path.join(pytest.TEST_CONFIGS_LOCATION, "testing_true_valid.toml")) as f:
#         config_contents = f.read()

#     tmp_f = tmp_path / "config.toml"

#     tmp_f.write_text(config_contents)

#     # TEST: Config file is created when no test_config is provided.
#     caplog.set_level(logging.INFO)
#     create_app(test_config=None, instance_path=tmp_path)
#     assert "Using this path as it's the first one that was found" in caplog.text


# def test_config_file_creation(tmp_path, caplog: pytest.LogCaptureFixture):
#     """TEST: that file is created when no config is provided.."""
#     with caplog.at_level(logging.WARNING):
#         create_app(test_config=None, instance_path=tmp_path)

#     assert "No configuration file found, creating at default location:" in caplog.text

