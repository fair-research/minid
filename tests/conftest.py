import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import fair_research_login
import globus_sdk
from minid import MinidClient

from minid.commands import main  # noqa -- ensures commands are loaded


@pytest.fixture
def logged_in(monkeypatch):
    load_mock = Mock()
    load_mock.return_value = {'auth.globus.org': 'mock_auth_tokens'}
    monkeypatch.setattr(MinidClient, 'is_logged_in', Mock(return_value=True))
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens',
                        load_mock)
    monkeypatch.setattr(fair_research_login.NativeClient, 'get_authorizers',
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
def mock_globus_sdk_auth(monkeypatch):
    mock_ac = Mock()
    monkeypatch.setattr(globus_sdk, 'AuthClient', mock_ac)
    return mock_ac


@pytest.fixture
def mock_get_cached_created_by(monkeypatch):
    gccb = Mock(return_value='Test User')
    monkeypatch.setattr(MinidClient, 'get_cached_created_by', gccb)
    return gccb


@pytest.fixture
def mocked_checksum(monkeypatch):
    mock_cc = Mock(return_value='mock_checksum')
    monkeypatch.setattr(MinidClient, 'compute_checksum', mock_cc)
    return mock_cc
