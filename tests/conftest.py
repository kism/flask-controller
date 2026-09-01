"""The conftest.py file serves as a means of providing fixtures for an entire directory.

Fixtures defined in a conftest.py can be used by any test in that package without needing to import them.

Tests should always use the tmp_path fixture as an instance_path so they don't pollute each other.
"""

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from webcontroller import create_app
from webcontroller.config import AppConf, Config

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from fastapi import FastAPI


@pytest.fixture
def config() -> Config:
    """Default config, with the socket sender thread disabled."""
    return Config(app=AppConf(run_socket=False))


@pytest.fixture
def app(tmp_path: Path, config: Config) -> FastAPI:
    """App with the default config, in a tmp_path instance directory."""
    return create_app(config=config, instance_path=tmp_path)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient]:
    """Test client for the app."""
    with TestClient(app) as test_client:
        yield test_client
