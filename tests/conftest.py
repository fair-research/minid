import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import fair_research_login
from minid import MinidClient

from minid.commands import main  # noqa -- ensures commands are loaded


@pytest.fixture
def logged_in(monkeypatch):
    load_mock = Mock()
    load_mock.return_value = {}
    monkeypatch.setattr(MinidClient, 'is_logged_in', Mock(return_value=True))
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens',
                        load_mock)
    return load_mock


@pytest.fixture
def logged_out(monkeypatch):
    mock_load = Mock()
    mock_load.side_effect = fair_research_login.LoadError()
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens',
                        mock_load)
    monkeypatch.setattr(MinidClient, 'is_logged_in', Mock(return_value=False))
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
