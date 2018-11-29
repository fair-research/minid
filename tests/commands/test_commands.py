import logging
import pytest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from minid.commands import cli
from minid.commands import auth
from minid.api import MinidClient


COMMANDS = [
    (
        ['login'],
        (auth.minid.auth, 'login'),
        ([], {'refresh_tokens': False,
              'no_local_server': False,
              'no_browser': False}
         )
    ),
    (
        ['login', '--remember-me'],
        (auth.minid.auth, 'login'),
        ([], {'refresh_tokens': True,
              'no_local_server': False,
              'no_browser': False}
         )
    ),
    (
        ['login', '--no-local-server'],
        (auth.minid.auth, 'login'),
        ([], {'refresh_tokens': False,
              'no_local_server': True,
              'no_browser': False}
         )
    ),
    (
        ['login', '--no-browser'],
        (auth.minid.auth, 'login'),
        ([], {'refresh_tokens': False,
              'no_local_server': False,
              'no_browser': True}
         )
    ),
    (
        ['version'], None, ([], {})
    ),
    (
        ['register', 'foo.txt'],
        (MinidClient, 'register'),
        ([], {'filename': 'foo.txt', 'locations': None,
              'test': False, 'title': None})
    ),
    (
        ['register', '--test', 'foo.txt'],
        (MinidClient, 'register'),
        ([], {'filename': 'foo.txt', 'locations': None,
              'test': True, 'title': None})
    ),
    (
        ['register', 'foo.txt', '--locations', 'http://example.com',
         'http://foo.example.com'],
        (MinidClient, 'register'),
        ([], {'filename': 'foo.txt', 'locations': ['http://example.com',
                                                   'http://foo.example.com'],
              'test': False, 'title': None})
    ),
    (
        ['register', 'foo.txt', '--title', 'My Foo'],
        (MinidClient, 'register'),
        ([], {'filename': 'foo.txt', 'locations': None,
              'test': False, 'title': 'My Foo'})
    ),
    (
        ['update', 'foo.txt', '--title', 'My Bar'],
        (MinidClient, 'update'),
        (['foo.txt'], {'locations': None, 'title': 'My Bar'})
    ),
    (
        ['update', 'foo.txt', '--locations', 'foobar.com'],
        (MinidClient, 'update'),
        (['foo.txt'], {'locations': ['foobar.com'], 'title': None})
    ),
    (
        ['check', 'ark:/99999/abcdefg'],
        (MinidClient, 'check'),
        (['ark:/99999/abcdefg'], {})
    ),
    (
        ['check', 'foobar.txt'],
        (MinidClient, 'check'),
        (['foobar.txt'], {})
    ),
]


@pytest.fixture(params=COMMANDS)
def client_command(request):
    return request.param


def _mock_function(monkeypatch, func_components):
    if not func_components:
        return None
    module, func_string = func_components
    func_mock = Mock()
    monkeypatch.setattr(module, func_string, func_mock)
    return func_mock


def test_command(monkeypatch, client_command):
    command, function, call_args = client_command
    mocked_function = _mock_function(monkeypatch, function)

    log = logging.getLogger(__name__)
    args = cli.cli.parse_args(command)
    cli.execute_command(cli, args, log)

    if mocked_function:
        f_args, f_kwargs = call_args
        mocked_function.assert_called_with(*f_args, **f_kwargs)
