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
import hashlib

from globus_sdk import NativeAppAuthClient
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer

from identifiers_client.identifiers_api import IdentifierClient
from identifiers_client.config import config as ic_config

from minid.auth import CLIENT_ID

log = logging.getLogger(__name__)


class MinidClient:

    NAME = 'Minid Client'
    NAMESPACE = 'kHAAfCby2zdn'
    TEST_NAMESPACE = 'HHxPIZaVDh9u'

    def __init__(self, token_set=None, on_refresh=None):
        """
        Create an identifier client. The client returned will depend on the
         token set used:
             token_set: None -- Only read access allowed
             token_set: Dict containing 'access_token' -- Temporary Client
             token_set: Dict containing 'access_token', 'refresh_token',
                        'at_expires' -- Refresh Client
         ** Parameters **
          ``token_set`` (* dict or None *)
          Tokens returned from an auth flow with the identifiers scope
          ``on_refresh`` (* function *)
          Function to call on refresh events when tokens expire. Useful for
          saving new tokens. Example: lambda tokens: save_my_tokens(tokens)
        """
        self.identifiers_client = self._get_identifier_client(token_set,
                                                              on_refresh)

    def _get_identifier_client(self, token_set, on_refresh):
        authorizer = None
        client = NativeAppAuthClient(CLIENT_ID,
                                     app_name=self.NAME)

        if token_set:
            refresh_requires = {'refresh_token', 'access_token', 'at_expires'}
            if refresh_requires.issubset(token_set):
                if on_refresh is not None or not callable(on_refresh):
                    raise ValueError('on_refresh is not a function!')
                authorizer = RefreshTokenAuthorizer(
                    token_set['refresh_token'],
                    client,
                    token_set['access_token'],
                    token_set['at_expires'],
                    on_refresh=on_refresh
                    )
            elif token_set.get('access_token'):
                authorizer = AccessTokenAuthorizer(token_set['access_token'])
        log.debug('Authorizer: {}'.format(authorizer))
        return IdentifierClient(
            "identifier",
            base_url=ic_config.get('client', 'service_url'),
            app_name=self.NAME,
            authorizer=authorizer
        )

    def register(self, filename, title='', locations=[], test=False):
        """
        ** Parameters **
          ``filename`` (*string*)
          The filename used to create a minid
          ``title`` (* string *)
          The title used to refer to the minid. Defaults to filename
          ``locations`` (* array of strings *)
          Network accessible locations for the given file
          ``test`` (* boolean *)
          Create the minid in a non-permanent test namespace
        """
        namespace = self.TEST_NAMESPACE if test is True else self.NAMESPACE
        metadata = {
            '_profile': 'erc',
            'erc.what': title or filename
        }
        checksums = [{
            'function': 'sha256',
            'value': self.compute_checksum(filename, hashlib.sha256())
        }]
        return self.identifiers_client.create_identifier(namespace=namespace,
                                                         visible_to=['public'],
                                                         metadata=metadata,
                                                         location=locations,
                                                         checksums=checksums
                                                         )

    def update(self, minid, title='', locations=[]):
        """
        ** Parameters **
          ``minid`` (*string*)
          The Minid to update
          ``title`` (* string *)
          The title used to refer to the minid. Defaults to filename
          ``locations`` (* array of strings *)
          Network accessible locations for the given file
          ``test`` (* boolean *)
          Create the minid in a non-permanent test namespace
        """
        metadata = {}
        if title:
            metadata['erc.what'] = title
        return self.identifiers_client.update_identifier(minid,
                                                         metadata=metadata,
                                                         location=locations)

    def check(self, minid):
        """
        ** Parameters **
          ``string`` (*string*)
          The Minid to check
        """
        return self.identifiers_client.get_identifier(minid)

    @staticmethod
    def compute_checksum(file_path, algorithm=None, block_size=65536):
        if not algorithm:
            algorithm = hashlib.sha256()
            log.debug("Using hash algorithm: {}".format(algorithm))

        log.debug('Computing checksum for {} using {}'.format(file_path,
                                                              algorithm))
        with open(os.path.abspath(file_path), 'rb') as open_file:
            buf = open_file.read(block_size)
            while len(buf) > 0:
                algorithm.update(buf)
                buf = open_file.read(block_size)
        open_file.close()
        return algorithm.hexdigest()
