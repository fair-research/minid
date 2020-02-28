# import os
# import time
# from copy import deepcopy
# import pytest
#
# from minid.config import Config
# from minid.exc import TokensExpired
#
#
# TEST_TOKENS = {
#     'my_service_org': {
#         'access_token': 'foobarbaz',
#         'expires_at_seconds': int(time.time()) + 60 * 60 * 24,
#         'refresh_token': None,
#         'resource_server': 'my_service_org',
#         'scope': 'https://auth.globus.org/scopes/my.serv.org/all_the_things',
#         'token_type': 'Bearer'
#     }
# }
#
#
# def test_base_config(mock_config):
#     """Assert basics about the config"""
#     assert mock_config.read.called
#     assert set(mock_config.sections()) == {'tokens', 'general'}
#     assert not mock_config.items('tokens')
#     assert not mock_config.items('general')
#
#
# def test_init_config(monkeypatch):
#     base_path_cfg = os.path.join(os.path.dirname(__file__), 'files',
#                                  'test_config.cfg')
#     test_cfg = os.path.abspath(base_path_cfg)
#     cfg = Config()
#     assert os.path.exists(test_cfg)
#     cfg.init_config(config_file=test_cfg)
#     assert set(cfg.sections()) == {'tokens', 'general'}
#     assert dict(cfg.items('tokens')) != {}
#     assert dict(cfg.items('general')) != {}
#
#
# def test_config_token_save_load(mock_config):
#     assert mock_config.items('tokens') == []
#     mock_config.save_tokens(TEST_TOKENS)
#     # Ensure all items were saved
#     assert mock_config.load_tokens() == TEST_TOKENS
#
#
# def test_config_expired_toknes(mock_config):
#     expired_tokens = deepcopy(TEST_TOKENS)
#     expired_tokens['my_service_org']['expires_at_seconds'] = \
#         int(time.time()) - 1
#     mock_config.save_tokens(expired_tokens)
#     with pytest.raises(TokensExpired):
#         mock_config.load_tokens()
