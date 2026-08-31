"""Test the cli entrypoint."""

import argparse
from typing import TYPE_CHECKING, Any

import waitress
from flask import Flask

from flaskcontroller import __main__

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TEST: The entrypoint builds an app and hands it to waitress, without actually serving."""
    mock_args = argparse.Namespace(host="127.0.0.1", port=5000, instance_path=tmp_path, threads=4)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    served: dict[str, Any] = {}
    monkeypatch.setattr(waitress, "serve", lambda app, **kwargs: served.update(app=app, **kwargs))

    __main__.main()

    assert isinstance(served["app"], Flask)
    assert served["port"] == 5000
    assert (tmp_path / "config.json").is_file()

    served["app"].extensions["controller"].stop()
