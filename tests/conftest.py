
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from minid.config import Config


@pytest.fixture()
def mock_config(monkeypatch):
    monkeypatch.setattr(Config, 'save', Mock())
    monkeypatch.setattr(Config, 'read', Mock())
    # monkeypatch.setattr(Config, 'CFG_DEFAULT', '')
    return Config()


@pytest.fixture(autouse=True)
def mock_logging():
    pass
