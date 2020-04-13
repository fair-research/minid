import pytest
import os
import json

from unittest.mock import Mock, mock_open, patch

import fair_research_login
import globus_sdk
from minid import MinidClient

BASE_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEST_RFM = os.path.join(BASE_DIR, 'mock_remote_file_manifest.json')
MOCK_IDENTIFIERS = os.path.join(BASE_DIR, 'mock_identifiers_response.json')

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
def mock_get_identifier(mock_identifiers_client, mock_globus_response):
    response = mock_globus_response()
    with open(MOCK_IDENTIFIERS) as f:
        response.data = json.load(f)
    mock_identifiers_client.get_identifier = Mock(return_value=response)
    return response


@pytest.fixture
def mock_gcs_register(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    mock_globus_response.data = {'identifier': 'newly_minted_identifier'}
    mock_identifiers_client.create_identifier.return_value = \
        mock_globus_response
    return mock_identifiers_client.create_identifier


@pytest.fixture
def mock_gcs_get_by_checksum(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    with open(MOCK_IDENTIFIERS) as f:
        mock_globus_response.data = json.load(f)
    mock_identifiers_client.get_identifier_by_checksum.return_value = \
        mock_globus_response
    return mock_identifiers_client.get_identifier_by_checksum


@pytest.fixture
def mocked_checksum(monkeypatch):
    mock_cc = Mock(return_value='mock_checksum')
    monkeypatch.setattr(MinidClient, 'compute_checksum', mock_cc)
    return mock_cc


@pytest.fixture
def mock_rfm():
    with open(TEST_RFM) as f:
        return json.load(f)


@pytest.fixture
def mock_globus_response():
    class MockGlobusSDKResponse(object):
        def __init__(self):
            self.data = {}

        def __getitem__(self, val):
            return self.data[val]
    return MockGlobusSDKResponse


@pytest.yield_fixture
def mock_streamed_rfm(mock_rfm):
    text = '\n'.join([json.dumps(l) for l in mock_rfm])
    with patch('builtins.open', mock_open(read_data=text)) as mocked_open:
        yield mocked_open
