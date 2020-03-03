import pytest
import os
import json

from mock import Mock, mock_open, patch

import fair_research_login
from minid import MinidClient

TEST_RFM = os.path.join(os.path.dirname(__file__), 'files',
                        'mock_remote_file_manifest.json')

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
def mock_gcs_register(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    mock_globus_response.data = {'identifier': 'newly_minted_identifier'}
    mock_identifiers_client.create_identifier.return_value = \
        mock_globus_response
    return mock_identifiers_client.create_identifier


@pytest.fixture
def mock_gcs_get_by_checksum(mock_identifiers_client, mock_globus_response):
    mock_globus_response = mock_globus_response()
    mock_globus_response.data = {'identifiers': []}
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
