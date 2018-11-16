"""
Copyright 2016 University of Chicago, University of Southern California

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import logging
from six.moves.configparser import ConfigParser
from collections import OrderedDict

from globus_sdk import serialize_token_groups, deserialize_token_groups

log = logging.getLogger(__name__)


class Config(ConfigParser):

    CFG_DEFAULT = os.path.join(os.path.expanduser('~'), '.minid',
                               'minid-config.cfg')
    CFG_FILENAME = CFG_DEFAULT
    ALLOWED_TOKENS = {'identifiers.globus.org'}
    #     'identifiers.globus.org': {
    #         'config_name': 'identifiers_globus_org_'
    #     }
    # }
    # TOKEN_HEADERS = {'access_token', 'refresh_token', 'resource_server',
    #                  'token_type', 'expires_at_seconds', 'scope'}

    def __init__(self):
        super(Config, self).__init__()
        self.init_config()

    def save(self):
        with open(self.CFG_FILENAME, 'w') as configfile:
            log.debug('Saving data to "{}"'.format(self.CFG_FILENAME))
            config.write(configfile)

    def load_tokens(self):
        try:
            return deserialize_token_groups(dict(self['tokens']))
        except:
            return {}

        # lookup = {cfg['config_name']: rs
        #           for cfg, rs in self.ALLOWED_TOKENS.items()}
        #
        # tokens = {}
        #
        # for key, value in self['tokens'].items():
        #     for cfg_prefix in lookup.keys():
        #         if key.startswith(cfg_prefix):
        #             stripped_key = key.relpace(cfg_prefix, '')
        #             if stripped_key not in self.TOKEN_HEADERS:
        #                 raise ValueError('{} is not a valid entry'.format(key))
        #             tokens[lookup[cfg_prefix]] = value
        #
        # log.debug('Successfully loaded {}'.format(tokens.keys()))

        # return tokens

    def save_tokens(self, tokens):
        #
        # if set(tokens.keys()) != set(self.ALLOWED_TOKENS.keys()):
        #     raise ValueError('{} not supported and cannot be saved'.format(
        #         set(tokens.keys()).difference(set(self.allowed_tokens.keys()))
        #     ))
        #
        # serialized_tokens = OrderedDict()
        # for rs, tks in tokens.items():
        #     if set(self.TOKEN_HEADERS) != set(tks):
        #         raise ValueError('{} must contain {}'
        #                          ''.format(rs, self.TOKEN_HEADERS))
        #     for ttype in self.TOKEN_HEADERS:
        #         tname = '{}{}'.format(self.ALLOWED_TOKENS[rs]['config_name'], ttype)
        #         tvalue = '' if tks[ttype] is None else str(tks[ttype])
        #         serialized_tokens[tname] = tvalue

        self['tokens'] = serialize_token_groups(tokens)
        self.save()

    def init_config(self, config_file=None):
        self.clear()
        self['tokens'] = {}
        self.CFG_FILENAME = config_file or self.CFG_DEFAULT
        if os.path.exists(self.CFG_FILENAME):
            self.read(self.CFG_FILENAME)


config = Config()
