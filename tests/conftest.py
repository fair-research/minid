import pytest
import os
import json

from unittest.mock import Mock, mock_open, patch

import fair_research_login
import globus_sdk
import minid

BASE_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEST_RFM = os.path.join(BASE_DIR, 'mock_remote_file_manifest.json')
TEST_RFM_IDENTIFIERS = os.path.join(BASE_DIR, 'mock_remote_file_manifest_identifiers.json')
MOCK_IDENTIFIERS = os.path.join(BASE_DIR, 'mock_identifiers_response.json')
MOCK_IDENTIFIERS_MULT = os.path.join(BASE_DIR, 'mock_identifiers_response_mult.json')


@pytest.fixture
def mock_fair_research_login(monkeypatch):
    tokens = {'auth.globus.org': 'mock_auth_tokens',
              'https://auth.globus.org/scopes/identifiers.fair-research.org/writer': 'mock_identifiers'}
    load_mock = Mock(return_value=tokens)
    monkeypatch.setattr(minid.MinidClient, 'is_logged_in', Mock(return_value=True))
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens', load_mock)
    auths = {name: globus_sdk.AccessTokenAuthorizer(token) for name, token in tokens.items()}
    monkeypatch.setattr(fair_research_login.NativeClient, 'get_authorizers', Mock(return_value=auths))
    monkeypatch.setattr(fair_research_login.NativeClient, 'get_authorizers_by_scope', Mock(return_value=auths))
    return fair_research_login.NativeClient


@pytest.fixture
def logged_in(monkeypatch, mock_fair_research_login):
    username = 'test_user@example.com'
    monkeypatch.setattr(minid.MinidClient, 'get_cached_created_by', Mock(return_value=username))
    return username


@pytest.fixture
def logged_out(monkeypatch):
    mock_load = Mock()
    mock_load.side_effect = fair_research_login.LoadError()
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens',
                        mock_load)
    monkeypatch.setattr(minid.MinidClient, 'is_logged_in', Mock(return_value=False))
    return mock_load


@pytest.fixture
def mock_cli(monkeypatch, mock_identifiers_client):
    cli = Mock()
    monkeypatch.setattr(minid.commands, 'get_client', Mock(return_value=cli))
    return cli


@pytest.fixture
def mock_identifiers_client(monkeypatch):
    mock_identifier = Mock()
    monkeypatch.setattr(minid.MinidClient, 'identifiers_client', mock_identifier)
    return mock_identifier


@pytest.fixture
def mock_globus_sdk_auth(monkeypatch):
    mock_ac = Mock()
    monkeypatch.setattr(globus_sdk, 'AuthClient', mock_ac)
    return mock_ac


@pytest.fixture
def mock_get_cached_created_by(monkeypatch):
    gccb = Mock(return_value='Test User')
    monkeypatch.setattr(minid.MinidClient, 'get_cached_created_by', gccb)
    return gccb


@pytest.fixture
def mock_identifier_response(mock_globus_response):
    response = mock_globus_response()
    with open(MOCK_IDENTIFIERS) as f:
        response.data = json.load(f)
    return response


@pytest.fixture
def mock_identifier_response_multiple(mock_globus_response):
    response = mock_globus_response()
    with open(MOCK_IDENTIFIERS_MULT) as f:
        response.data = json.load(f)
    return response


@pytest.fixture
def mock_get_identifier(mock_identifiers_client, mock_identifier_response):
    mock_identifiers_client.get_identifier = Mock(return_value=mock_identifier_response)
    return mock_identifiers_client


@pytest.fixture
def mock_gcs_register(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    mock_globus_response.data = {'identifier': 'newly_minted_identifier'}
    mock_identifiers_client.create_identifier.return_value = \
        mock_globus_response
    return mock_identifiers_client.create_identifier


@pytest.fixture
def mock_gcs_update(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    mock_globus_response.data = {'identifier': 'updated_identifier'}
    mock_identifiers_client.update_identifier.return_value = \
        mock_globus_response
    return mock_identifiers_client.update_identifier


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
    monkeypatch.setattr(minid.MinidClient, 'compute_checksum', mock_cc)
    return mock_cc


@pytest.fixture
def mock_rfm_filename():
    return TEST_RFM


@pytest.fixture
def mock_rfm_identifiers_filename():
    return TEST_RFM_IDENTIFIERS


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
    text = '\n'.join([json.dumps(rfm) for rfm in mock_rfm])
    with patch('builtins.open', mock_open(read_data=text)) as mocked_open:
        yield mocked_open
