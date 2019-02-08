import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from native_login import LoadError
from minid import MinidClient

from minid.commands import main  # noqa -- ensures commands are loaded


@pytest.fixture
def logged_out(monkeypatch):
    mock_load = Mock()
    mock_load.side_effect = LoadError()
    monkeypatch.setattr(MinidClient, 'load_tokens', mock_load)
    return mock_load


@pytest.fixture
def mock_identifiers_client(monkeypatch):
    mock_identifier = Mock()
    monkeypatch.setattr(MinidClient, 'identifiers_client', mock_identifier)
    return mock_identifier


@pytest.fixture
def mocked_checksum(monkeypatch):
    mock_cc = Mock(return_value='mock_checksum')
    monkeypatch.setattr(MinidClient, 'compute_checksum', mock_cc)
    return mock_cc
