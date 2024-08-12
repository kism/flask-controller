"""Test versioning."""

import tomlkit

import flaskcontroller


def test_version():
    """Test version variable."""
    with open("pyproject.toml", "rb") as f:
        pyproject_toml = tomlkit.load(f)
    assert pyproject_toml["tool"]["poetry"]["version"] == flaskcontroller.__version__
