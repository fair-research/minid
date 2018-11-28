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
import time
from six.moves.configparser import ConfigParser

from globus_sdk import serialize_token_groups, deserialize_token_groups

from minid.exc import TokensExpired

log = logging.getLogger(__name__)


class Config(ConfigParser):

    CFG_DEFAULT = os.path.join(os.path.expanduser('~'), '.minid',
                               'minid-config.cfg')
    CFG_FILENAME = CFG_DEFAULT
    ALLOWED_TOKENS = {'identifiers.globus.org'}

    def __init__(self):
        # Do not use super(Config, self), ConfigParser is an old-style class
        ConfigParser.__init__(self)
        self.init_config()

    def save(self):
        with open(self.CFG_FILENAME, 'w') as configfile:
            log.debug('Saving data to "{}"'.format(self.CFG_FILENAME))
            config.write(configfile)

    def load_tokens(self):
        tokens = {}
        try:
            tokens = deserialize_token_groups(dict(self.items('tokens')))
        except:
            return tokens

        if any([self.check_tokens_expired(ts) for ts in tokens.values()]):
            raise TokensExpired()
        return tokens

    def save_tokens(self, tokens):
        for name, value in serialize_token_groups(tokens).items():
            self.set('tokens', name, value)
        self.save()

    def init_config(self, config_file=None):
        for sec in self.sections():
            self.remove_section(sec)
        self.CFG_FILENAME = config_file or self.CFG_DEFAULT
        if os.path.exists(self.CFG_FILENAME):
            self.read(self.CFG_FILENAME)
        for required_section in ['general', 'tokens']:
            if required_section not in self.sections():
                self.add_section(required_section)

    @staticmethod
    def check_tokens_expired(token_set):
        return time.time() >= token_set["expires_at_seconds"]


config = Config()
