import os
from minid.minid import MinidClient


def test_load_logged_out_authorizer(logged_out):
    cli = MinidClient()
    assert cli.identifiers_client.authorizer is None


def test_register(mock_identifiers_client, mocked_checksum):
    cli = MinidClient()
    cli.register('foo.txt')

    expected = {
        'checksums': [{'function': 'sha256', 'value': 'mock_checksum'}],
        'metadata': {
            '_profile': 'erc',
            'erc.what': 'foo.txt'
        },
        'location': [],
        'namespace': MinidClient.NAMESPACE,
        'visible_to': ['public']
    }
    assert expected in mock_identifiers_client.create_identifier.call_args


def test_update(mock_identifiers_client, mocked_checksum):
    cli = MinidClient()
    cli.update('ark:/99999/mock-ark', title='foo.txt',
               locations=['http://example.com'])
    mock_identifiers_client.update_identifier.assert_called_with(
        'ark:/99999/mock-ark',
        metadata={'erc.what': 'foo.txt'},
        location=['http://example.com']
    )


def test_check(mock_identifiers_client, mocked_checksum):
    cli = MinidClient()
    cli.check('ark:/99999/mock-ark')
    mock_identifiers_client.get_identifier.assert_called_with(
        'ark:/99999/mock-ark',
    )


def test_compute_checksum():
    # Prehashed sum with openssl, file contents "12345"
    sum = '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'
    path = os.path.join(os.path.dirname(__file__), 'files',
                        'test_compute_checksum.txt')
    assert MinidClient.compute_checksum(path) == sum
