import pytest
import hashlib
import os
from minid.minid import MinidClient
from minid.exc import MinidException

from unittest.mock import Mock

TEST_CHECKSUM_FILE = os.path.join(os.path.dirname(__file__), 'files',
                                  'test_compute_checksum.txt')
TEST_CHECKSUM_VALUE = ('5994471abb01112afcc18159f6cc74b4'
                       'f511b99806da59b3caf5a9c173cacfc5')


def test_load_logged_out_authorizer(logged_out):
    assert MinidClient().identifiers_client.authorizer is None


def test_register(mock_identifiers_client, mocked_checksum, logged_in,
                  mock_get_cached_created_by):
    cli = MinidClient()
    cli.register('foo.txt')

    expected = {
        'checksums': [{'function': 'sha256', 'value': 'mock_checksum'}],
        'metadata': {
            'title': 'foo.txt',
            'length': 21,
            'created_by': 'Test User',
        },
        'location': [],
        'namespace': MinidClient.NAMESPACE,
        'visible_to': ['public']
    }
    assert expected in mock_identifiers_client.create_identifier.call_args


def test_update(mock_identifiers_client, mocked_checksum, logged_in):
    cli = MinidClient()
    cli.update('hdl:20.500.12633/mock-hdl', title='foo.txt',
               locations=['http://example.com'])
    mock_identifiers_client.update_identifier.assert_called_with(
        'hdl:20.500.12633/mock-hdl',
        metadata={'title': 'foo.txt'},
        location=['http://example.com']
    )


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
