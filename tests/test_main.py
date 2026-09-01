"""Test the cli entrypoint."""

import argparse
import json
from typing import TYPE_CHECKING, Any

import uvicorn
from fastapi import FastAPI

from webcontroller import __main__

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TEST: The entrypoint builds an app and hands it to uvicorn, without actually serving."""
    mock_args = argparse.Namespace(host="127.0.0.1", port=5000, instance_path=tmp_path, dump_openapi=False)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    served: dict[str, Any] = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: served.update(app=app, **kwargs))

    __main__.main()

    assert isinstance(served["app"], FastAPI)
    assert served["port"] == 5000
    assert (tmp_path / "config.json").is_file()

    served["app"].state.controller.stop()


def test_main_dump_openapi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """TEST: --dump-openapi prints the schema to stdout and doesn't touch the instance directory."""
    mock_args = argparse.Namespace(host="127.0.0.1", port=5000, instance_path=tmp_path, dump_openapi=True)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", lambda self: mock_args)

    __main__.main()

    assert json.loads(capsys.readouterr().out)["paths"].keys() >= {"/status", "/input"}
    assert not (tmp_path / "config.json").exists()
