import pytest
import hashlib
import os
import sys
from minid.minid import MinidClient
from minid.exc import MinidException

from unittest.mock import Mock, call

FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')
TEST_RFM_FILE = os.path.join(FILES_DIR, 'mock_remote_file_manifest.json')
TEST_CHECKSUM_FILE = os.path.join(FILES_DIR, 'test_compute_checksum.txt')
TEST_CHECKSUM_VALUE = ('5994471abb01112afcc18159f6cc74b4'
                       'f511b99806da59b3caf5a9c173cacfc5')


def test_load_logged_out_authorizer(logged_out):
    assert MinidClient().identifiers_client.authorizer is None


def test_client_creates_config_dir_if_not_exists(monkeypatch):
    mkdir = Mock()
    monkeypatch.setattr(os, 'mkdir', mkdir)
    monkeypatch.setattr(os.path, 'exists', Mock(return_value=False))
    MinidClient()
    assert mkdir.called


def test_register(mock_identifiers_client, mocked_checksum, logged_in,
                  mock_get_cached_created_by, monkeypatch):
    stat = Mock()
    stat.return_value.st_size = 21
    monkeypatch.setattr(os, 'stat', stat)
    cli = MinidClient()
    cli.register_file('foo.txt')

    expected = {
        'checksums': [{'function': 'sha256', 'value': 'mock_checksum'}],
        'metadata': {
            'title': 'foo.txt',
            'length': 21,
            'created_by': 'Test User',
        },
        'location': [],
        'namespace': MinidClient.IDENTIFIERS_NAMESPACE,
        'visible_to': ['public'],
        'replaces': None,
    }
    assert expected in mock_identifiers_client.create_identifier.call_args


def test_register_unsupported_checksum(mock_identifiers_client, logged_in):
    cli = MinidClient()
    checksums = [{'function': 'sha256', 'value': 'mock_checksum'},
                 {'function': 'NOT_REAL', 'value': 'irrelevant!'}]
    cli.register(checksums, title='foo.txt')

    expected = {
        'checksums': [{'function': 'sha256', 'value': 'mock_checksum'}],
        'metadata': {
            'title': 'foo.txt'
        },
        'location': [],
        'namespace': MinidClient.IDENTIFIERS_NAMESPACE,
        'visible_to': ['public'],
    }
    assert expected in mock_identifiers_client.create_identifier.call_args


def test_register_replaces(mock_identifiers_client, logged_in):
    cli = MinidClient()
    checksums = [{'function': 'sha256', 'value': 'mock_checksum'}]
    cli.register(checksums, title='foo.txt', replaces='minid:123456')

    expected = {
        'checksums': [{'function': 'sha256', 'value': 'mock_checksum'}],
        'metadata': {
            'title': 'foo.txt'
        },
        'location': [],
        'namespace': MinidClient.IDENTIFIERS_NAMESPACE,
        'visible_to': ['public'],
        'replaces': 'hdl:20.500.12582/123456'
    }
    assert expected in mock_identifiers_client.create_identifier.call_args


def test_get_most_recent_active_entity(mock_rfm, logged_in,
                                       mock_gcs_get_by_checksum,
                                       mock_gcs_register):
    first = mock_gcs_get_by_checksum.return_value.data['identifiers'][0]
    second = first.copy()
    second['created'] = '2030-05-03T16:48:03.463187'
    second['updated'] = '2030-05-03T16:48:03.463187'
    second['identifier'] = 'hdl:20.500.12633/the-newest-one'
    cli = MinidClient()
    assert cli.get_most_recent_active_entity([first, second]) == second
    assert cli.get_most_recent_active_entity([second, first]) == second


def test_get_or_register_manifest_entity(
        mock_rfm, logged_in, mock_gcs_get_by_checksum, mock_gcs_register):
    cli = MinidClient()
    # Set no pre-existing identifiers so we can register one
    mock_gcs_get_by_checksum.return_value.data['identifiers'] = []
    cli.get_or_register_rfm(mock_rfm[0], True)
    assert mock_gcs_register.called
    assert mock_gcs_get_by_checksum.called


def test_get_or_register_manifest_entity_with_preregistered(
        mock_rfm, logged_in, mock_gcs_get_by_checksum, mock_gcs_register):
    cli = MinidClient()
    cli.get_or_register_rfm(mock_rfm[0], True)
    assert mock_gcs_register.called is False
    assert mock_gcs_get_by_checksum.called


def test_get_or_register_manifest_entry_with_no_matching_hashes(
        mock_rfm, logged_in, mock_gcs_get_by_checksum, mock_gcs_register):
    # Should not return any minids
    mock_gcs_get_by_checksum.return_value.data['identifiers'] = []
    # Set custom hash
    record = mock_rfm[0]
    del record['sha256']
    record['sha512'] = 'abcdefg_sha512hash_hijklmnop'
    cli = MinidClient()
    cli.get_or_register_rfm(record, True)
    assert mock_gcs_register.called
    assert mock_gcs_get_by_checksum.called


def test_batch_register(monkeypatch, logged_in, mock_rfm, mock_gcs_register,
                        mock_gcs_get_by_checksum):
    mock_gcs_get_by_checksum.return_value.data['identifiers'] = []
    cli = MinidClient()
    cli.batch_register(TEST_RFM_FILE, True)
    assert mock_gcs_register.call_count == len(mock_rfm)


def test_batch_register_pre_existing(monkeypatch, logged_in, mock_rfm,
                                     mock_gcs_register,
                                     mock_gcs_get_by_checksum):
    cli = MinidClient()
    cli.batch_register(TEST_RFM_FILE, True)
    # Mocked identifiers should match exactly the batch registered identifiers
    assert mock_gcs_register.call_count == 0


def test_update(mock_identifiers_client, mocked_checksum, logged_in):
    cli = MinidClient()
    cli.update('hdl:20.500.12633/mock-hdl', title='foo.txt',
               locations=['http://example.com'])
    mock_identifiers_client.update_identifier.assert_called_with(
        'hdl:20.500.12633/mock-hdl',
        metadata={'title': 'foo.txt'},
        location=['http://example.com']
    )


def test_update_invalid_args(mock_identifiers_client, logged_in):
    cli = MinidClient()
    with pytest.raises(MinidException):
        cli.update('hdl:20.500.12633/1234567', non_existant_arg='foobar')


def test_update_translates_hdls(mock_identifiers_client, logged_in):
    cli = MinidClient()

    cli.update('minid:first', replaces='minid:second', replaced_by='minid:thd')
    expected = call('hdl:20.500.12582/first',
                    replaces='hdl:20.500.12582/second',
                    replaced_by='hdl:20.500.12582/thd',
                    metadata={})
    assert mock_identifiers_client.update_identifier.called
    assert mock_identifiers_client.update_identifier.call_args == expected


def test_check(mock_identifiers_client, mocked_checksum):
    cli = MinidClient()
    cli.check('hdl:20.500.12633/mock-hdl')
    mock_identifiers_client.get_identifier.assert_called_with(
        'hdl:20.500.12633/mock-hdl',
    )


def test_check_by_checksum(mock_identifiers_client):
    cli = MinidClient()
    cli.check(TEST_CHECKSUM_FILE)
    mock_identifiers_client.get_identifier_by_checksum.assert_called_with(
        TEST_CHECKSUM_VALUE,
    )


def test_checksumming_file_does_not_exist():
    cli = MinidClient()
    with pytest.raises(MinidException):
        cli.check('does_not_exist.txt')


def test_fs_error_during_checksum(monkeypatch):
    cli = MinidClient()
    hasher_inst = Mock()
    hasher_inst.update.side_effect = Exception
    monkeypatch.setattr(hashlib, 'sha256', Mock(return_value=hasher_inst))
    with pytest.raises(MinidException):
        cli.check(TEST_CHECKSUM_FILE)


def test_unrecognized_algorithm():
    with pytest.raises(MinidException):
        MinidClient.get_algorithm('not_elliptical_enough')


def test_compute_checksum():
    # Prehashed sum with openssl, file contents "12345"
    checksum = MinidClient.compute_checksum(TEST_CHECKSUM_FILE)
    assert checksum == TEST_CHECKSUM_VALUE


def test_get_cached_created_by(mock_globus_sdk_auth, logged_in):
    mc = MinidClient()
    mc.get_cached_created_by()
    assert mock_globus_sdk_auth.called


def test_get_cached_created_by_is_cached(mock_globus_sdk_auth, logged_in):
    mc = MinidClient()
    mc.get_cached_created_by()
    mc.get_cached_created_by()
    assert mock_globus_sdk_auth.call_count == 1


def test_read_manifest_entries(mock_rfm):
    read_rfm = list(MinidClient.read_manifest_entries(TEST_RFM_FILE))
    assert read_rfm == mock_rfm


def test_is_stream(mock_streamed_rfm):
    with open('magic_file.json', 'r') as manifest:
        assert MinidClient._is_stream(manifest) is True


def test_is_not_stream():
    with open(TEST_RFM_FILE, 'r') as manifest:
        assert MinidClient._is_stream(manifest) is False


@pytest.mark.skipif(sys.version_info > (3, 6) and sys.version_info < (3, 7),
                    reason='Skip if python 3.6')
def test_read_manifest_entries_streamed(mock_streamed_rfm, mock_rfm,
                                        monkeypatch):
    monkeypatch.setattr(MinidClient, '_is_stream', Mock(return_value=True))
    read_rfm = list(MinidClient.read_manifest_entries('rfm.json'))
    assert len(read_rfm) == len(mock_rfm)
    assert read_rfm == mock_rfm
