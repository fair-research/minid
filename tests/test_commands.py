import traceback
import pytest

from unittest.mock import Mock
import click
from click.testing import CliRunner
from minid.commands import main, minid_ops, formatting
from fair_identifiers_client.identifiers_api import IdentifierClientError

import minid

LOGGED_IN_COMMANDS = [
    ({
        # The command to run in the cli
        'command': ['login'],
        # The function to mock and test
        'mock': None,
        # Assert that the mocked function above was called with these args
        'expected_call_args': ([], {})
    }),
    ({
        'command': ['login', '--force'],
        'mock': (minid.MinidClient, 'login'),
        'expected_call_args': ([], {
            'refresh_tokens': False,
            'no_local_server': False,
            'no_browser': False,
            'force': True,
        })
    }),
    ({
        'command': ['logout'],
        'mock': (minid.MinidClient, 'logout'),
        'expected_call_args': ([], {})
    }),
    ({
        'command': ['version'],
        'mock': None,
        'expected_call_args': ([], {})
    }),
    ({
        'command': ['register', 'foo.txt'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'test': False,
            'title': None
        })
    }),
    ({
        'command': ['register', '--json', 'foo.txt'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'test': False,
            'title': None
        })
    }),
    ({
        'command': ['register', '--test', 'foo.txt'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'test': True,
            'title': None
        })
    }),
    ({
        'command': [
            'register', 'foo.txt', '--locations', 'http://example.com,http://foo.example.com'
        ],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'locations': [
                'http://example.com', 'http://foo.example.com'
            ],
            'test': False,
            'title': None
        })
    }),
    ({
        'command': ['register', 'foo.txt', '--title', 'My Foo'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'test': False,
            'title': 'My Foo'
        })
    }),
    ({
        'command': ['update', 'minid:123', '--title', 'My Bar'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'title': 'My Bar'
        })
    }),
    ({
        'command': ['update', 'minid:123', '--locations', 'foobar.com'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'locations': ['foobar.com'], 'title': None
        })
    }),
    ({
        'command': ['update', 'minid:123', '--locations', 'None'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'locations': [], 'title': None
        })
    }),
    ({
        'command': ['update', 'minid:123', '--replaced-by', 'None'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'replaced_by': None, 'title': None
        })
    }),
    ({
        'command': ['update', 'minid:123', '--replaces', 'None'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'replaces': None, 'title': None
        })
    }),
    ({
        'command': ['update', 'minid:123', '--set-active'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {'title': None, 'active': True})
    }),
    ({
        'command': ['update', 'minid:123', '--set-inactive'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {'title': None, 'active': False})
    }),
    ({
        'command': ['update', 'minid:123', '--replaces', 'None',
                    '--replaced-by', 'None', '--locations', 'None'],
        'mock': (minid.MinidClient, 'update'),
        'expected_call_args': (['minid:123'], {
            'replaced_by': None, 'title': None, 'locations': [],
            'replaces': None
        })
    }),
    ({
        'command': ['check', 'ark:/99999/abcdefg'],
        'mock': (minid.MinidClient, 'check'),
        'expected_call_args': (['ark:/99999/abcdefg', 'sha256'], {})
    }),
    ({
        'command': ['check', 'foobar.txt'],
        'mock': (minid.MinidClient, 'check'),
        'expected_call_args': (['foobar.txt', 'sha256'], {})
    }),
]

LOGGED_OUT_COMMANDS = [
    ({
        # The command to run in the cli
        'command': ['login'],
        # The function to mock and test
        'mock': (minid.MinidClient, 'login'),
        # Assert that the mocked function above was called with these args
        'expected_call_args': ([], {
            'refresh_tokens': False,
            'no_local_server': False,
            'no_browser': False,
            'force': False,
        })
    }),
    ({
        'command': ['login', '--remember-me'],
        'mock': (minid.MinidClient, 'login'),
        'expected_call_args': ([], {
            'refresh_tokens': True,
            'no_local_server': False,
            'no_browser': False,
            'force': False,
        })
    }),
    ({
        'command': ['login', '--no-local-server'],
        'mock': (minid.MinidClient, 'login'),
        'expected_call_args': ([], {
            'refresh_tokens': False,
            'no_local_server': True,
            'no_browser': False,
            'force': False,
        })
    }),
    ({
        'command': ['login', '--no-browser'],
        'mock': (minid.MinidClient, 'login'),
        'expected_call_args': ([], {
            'refresh_tokens': False,
            'no_local_server': False,
            'no_browser': True,
            'force': False,
        })
    }),
    ({
        'command': ['logout'],
        'mock': None,
        'expected_call_args': ([], {})
    }),
]


@pytest.fixture
def mock_ic_error(monkeypatch):
    mock_request = Mock()
    mock_request.status_code = 401
    mock_request.headers = {'Content-Type': 'application/json'}
    mock_request.json.return_value = {'error': ['error'], 'code': 'foo',
                                      'message': 'foo'}
    return IdentifierClientError(mock_request)


@pytest.fixture
def mock_print(monkeypatch):
    monkeypatch.setattr(minid_ops, 'print_minids', Mock())


def _mock_function(monkeypatch, func_components):
    if not func_components:
        return None
    module, func_string = func_components
    func_mock = Mock()
    monkeypatch.setattr(module, func_string, func_mock)
    return func_mock


@pytest.fixture(params=LOGGED_IN_COMMANDS)
def cli_command_logged_in(request, logged_in, mock_print):
    return request.param


@pytest.fixture(params=LOGGED_OUT_COMMANDS)
def cli_command_logged_out(request, logged_out):
    return request.param


def execute_and_test_command(monkeypatch, cli_command):
    mocked_function = _mock_function(monkeypatch, cli_command['mock'])

    runner = CliRunner()
    result = runner.invoke(main.cli, cli_command['command'])
    if result.exc_info:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0

    if mocked_function is not None:
        f_args, f_kwargs = cli_command['expected_call_args']
        mocked_function.assert_called_with(*f_args, **f_kwargs)


def test_logged_in_commands(monkeypatch, cli_command_logged_in):
    execute_and_test_command(monkeypatch, cli_command_logged_in)


def test_logged_out_commands(monkeypatch, cli_command_logged_out):
    execute_and_test_command(monkeypatch, cli_command_logged_out)


def test_command_requires_login(logged_out):
    runner = CliRunner()
    result = runner.invoke(main.cli, ['register', '--test', 'foo.txt'])
    traceback.print_exception(*result.exc_info)
    assert result.exit_code == 1


def test_pretty_print(mock_identifier_response):
    identifier = mock_identifier_response.data['identifiers'][0]
    m = formatting.pretty_format_minid(minid.minid.MinidClient, identifier)
    print(formatting.get_local_datetime(identifier['created']))
    assert 'Wednesday, April 08, 2020' in m
    assert 'Thursday, April 09, 2020' in m
    assert 'minid.test' in m


def test_print_minids(mock_identifier_response, mock_identifier_response_multiple, monkeypatch):
    clecko = Mock()
    monkeypatch.setattr(click, 'echo', clecko)
    minid_ops.print_minids(mock_identifier_response.data)
    assert clecko.called
    minid_ops.print_minids(mock_identifier_response_multiple.data)
    assert clecko.call_count == 2


def test_print_minids_json(mock_identifier_response, monkeypatch):
    clecko = Mock()
    monkeypatch.setattr(click, 'echo', clecko)
    minid_ops.print_minids(mock_identifier_response.data, output_json=True)
    assert clecko.called


def test_batch_register(logged_in, mock_rfm, mock_rfm_filename, mock_gcs_register,
                        mock_gcs_get_by_checksum):
    mock_gcs_get_by_checksum.return_value.data['identifiers'] = []

    runner = CliRunner()
    result = runner.invoke(main.cli, ['batch-register', mock_rfm_filename])
    assert result.exit_code == 0
    assert mock_gcs_register.call_count == len(mock_rfm)


def test_cli_update_active_invalid(logged_in):
    runner = CliRunner()
    result = runner.invoke(main.cli, ['update', 'minid:123', '--set-active', '--set-inactive'])
    assert result.exit_code == 1
    assert 'Cannot use both' in result.output


def test_cli_update_none_values(logged_in, mock_print, mock_cli):
    mock_cli.update.side_effect = minid.exc.UnknownIdentifier()
    runner = CliRunner()
    result = runner.invoke(main.cli, ['update', 'minid:123', '--locations', 'none'])
    traceback.print_exception(*result.exc_info)
    assert mock_cli.update.called
    assert result.exit_code == 1


# def test_cli_errors(logged_out):
#     # Raises Logout Error
#     args = cli.cli.parse_args(['register', '--test', 'foo.txt'])
#     cli.execute_command(cli, args, Mock())
#     args = cli.cli.parse_args(['--json', 'register', '--test', 'foo.txt'])
#     cli.execute_command(cli, args, Mock())


def test_file_not_found(logged_in, monkeypatch):
    runner = CliRunner()
    result = runner.invoke(main.cli, ['register', 'not_found.txt'])
    traceback.print_exception(*result.exc_info)
    assert result.exit_code == 1


def test_command_general_identifiers_error(monkeypatch, logged_in,
                                           mock_ic_error):
    mock_ic_error.http_status = 500
    register_mock = Mock(side_effect=mock_ic_error)
    monkeypatch.setattr(minid.minid.MinidClient, 'register_file', register_mock)

    runner = CliRunner()
    result = runner.invoke(main.cli, ['register', '--test', 'foo.txt'])
    traceback.print_exception(*result.exc_info)
    assert result.exit_code == 1
    assert register_mock.called
