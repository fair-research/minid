import pytest
from unittest.mock import Mock

import fair_research_login

from minid.minid import MinidClient
from minid.exc import LoginRequired


@pytest.fixture
def mock_load_tokens(monkeypatch):
    load_tokens = Mock()
    monkeypatch.setattr(fair_research_login.NativeClient, 'load_tokens',
                        load_tokens)
    return load_tokens


@pytest.fixture
def mock_load_tokens_error(mock_load_tokens):
    mock_load_tokens.side_effect = fair_research_login.exc.LoadError
    return mock_load_tokens


@pytest.fixture
def mock_auth_logout(monkeypatch):
    logout = Mock()
    monkeypatch.setattr(fair_research_login.NativeClient, 'logout',
                        logout)
    return logout


@pytest.fixture(params=['register', 'update'])
def minid_auth_required_op(request, logged_out):
    return request.param


def test_command_requires_login(minid_auth_required_op):
    mc = MinidClient()
    cmd = getattr(mc, minid_auth_required_op)
    with pytest.raises(LoginRequired):
        cmd('mock_arg')


def test_minid_sdk_login(mock_load_tokens):
    mc = MinidClient()
    mc.login()
    assert mock_load_tokens.called


def test_minid_logout(mock_load_tokens, mock_auth_logout):
    mc = MinidClient()
    mc.logout()
    assert mock_auth_logout.called


def test_minid_logout_after_logout(mock_load_tokens_error, mock_auth_logout):
    mc = MinidClient()
    mc.logout()
    assert not mock_auth_logout.called


def test_custom_authorizer():
    inst_authorizer = Mock()
    mc = MinidClient(authorizer=inst_authorizer)
    assert mc.authorizer == inst_authorizer

    settr_authorizer = Mock()
    mc.authorizer = settr_authorizer
    assert mc.authorizer == settr_authorizer
