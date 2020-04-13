import logging
import pytest

from unittest.mock import Mock
from fair_identifiers_client.identifiers_api import IdentifierClientError

from minid.commands import cli
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
        'mock': None,
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
            'locations': None,
            'test': False,
            'title': None
        })
    }),
    ({
        'command': ['--json', 'register', 'foo.txt'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'locations': None,
            'test': False,
            'title': None
        })
    }),
    ({
        'command': ['register', '--test', 'foo.txt'],
        'mock': (minid.MinidClient, 'register_file'),
        'expected_call_args': (['foo.txt'], {
            'locations': None,
            'test': True,
            'title': None
        })
    }),
    ({
        'command': [
            'register', 'foo.txt', '--locations', 'http://example.com',
            'http://foo.example.com'
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
            'locations': None,
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


def _mock_function(monkeypatch, func_components):
    if not func_components:
        return None
    module, func_string = func_components
    func_mock = Mock()
    monkeypatch.setattr(module, func_string, func_mock)
    return func_mock


@pytest.fixture(params=LOGGED_IN_COMMANDS)
def cli_command_logged_in(request, logged_in):
    return request.param


@pytest.fixture(params=LOGGED_OUT_COMMANDS)
def cli_command_logged_out(request, logged_out):
    return request.param


def execute_and_test_command(monkeypatch, cli_command):
    mocked_function = _mock_function(monkeypatch, cli_command['mock'])

    log = logging.getLogger(__name__)
    args = cli.cli.parse_args(cli_command['command'])
    cli.execute_command(cli, args, log)

    if mocked_function is not None:
        f_args, f_kwargs = cli_command['expected_call_args']
        mocked_function.assert_called_with(*f_args, **f_kwargs)


def test_logged_in_commands(monkeypatch, cli_command_logged_in):
    execute_and_test_command(monkeypatch, cli_command_logged_in)


def test_logged_out_commands(monkeypatch, cli_command_logged_out):
    execute_and_test_command(monkeypatch, cli_command_logged_out)


def test_command_requires_login(monkeypatch, logged_out, mock_ic_error):
    register_mock = Mock()
    register_mock.side_effect = mock_ic_error
    monkeypatch.setattr(minid.minid.MinidClient, 'register_file',
                        register_mock)

    log = Mock()
    args = cli.cli.parse_args(['register', '--test', 'foo.txt'])
    cli.execute_command(cli, args, log)

    assert register_mock.called


def test_command_requires_login_json_output(monkeypatch, logged_in,
                                            mock_ic_error):
    register_mock = Mock()
    register_mock.side_effect = mock_ic_error
    monkeypatch.setattr(minid.minid.MinidClient, 'register_file',
                        register_mock)

    log = Mock()
    args = cli.cli.parse_args(['--json', 'register', '--test', 'foo.txt'])
    cli.execute_command(cli, args, log)

    assert register_mock.called


def test_command_print_help():
    with pytest.raises(SystemExit):
        args = cli.cli.parse_args(['register'])
        cli.execute_command(cli, args, Mock())


def test_pretty_print(mock_get_identifier, monkeypatch):
    # No assertions are made here. Basically, we want to make sure pretty
    # print does not throw errors.
    identifier = mock_get_identifier.data['identifiers'][0]
    cli.pretty_print_minid(minid.minid.MinidClient, identifier)


def test_cli_print_minid(mock_get_identifier, monkeypatch):
    """Test printing minids. Ensure that pretty print was called and the CLI
    didn't bail out early due to another error."""
    pretty_print_minid = Mock()
    monkeypatch.setattr(cli, 'pretty_print_minid', pretty_print_minid)
    args = cli.cli.parse_args(['--verbose', 'check', 'minid.test:123456'])
    cli.execute_command(cli, args, Mock())
    assert pretty_print_minid.called


def test_cli_update_none_values(logged_in, mock_identifiers_client):
    update = Mock()
    mock_identifiers_client.update = update

    args = cli.cli.parse_args(['update', 'minid:123', '--locations', 'none'])
    cli.execute_command(cli, args, Mock())

    assert not mock_identifiers_client.called


def test_cli_errors(logged_out):
    # Raises Logout Error
    args = cli.cli.parse_args(['register', '--test', 'foo.txt'])
    cli.execute_command(cli, args, Mock())
    args = cli.cli.parse_args(['--json', 'register', '--test', 'foo.txt'])
    cli.execute_command(cli, args, Mock())


def test_file_not_found(logged_in, monkeypatch):
    log = Mock()
    monkeypatch.setattr(cli, 'log', log)
    args = cli.cli.parse_args(['register', 'not_found.txt'])
    cli.execute_command(cli, args, Mock())
    assert log.error.called


def test_command_general_identifiers_error(monkeypatch, logged_in,
                                           mock_ic_error):
    mock_ic_error.http_status = 500
    register_mock = Mock()
    register_mock.side_effect = mock_ic_error
    monkeypatch.setattr(minid.minid.MinidClient, 'register_file',
                        register_mock)

    log = Mock()
    args = cli.cli.parse_args(['--verbose', 'register', '--test', 'foo.txt'])
    cli.execute_command(cli, args, log)

    assert register_mock.called
