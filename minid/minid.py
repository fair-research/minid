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

from fair_research_login import (NativeClient,
                                 ConfigParserTokenStorage,
                                 LoadError)

from identifiers_client.identifiers_api import IdentifierClient
from identifiers_client.config import config as ic_config

log = logging.getLogger(__name__)


class MinidClient(NativeClient):
    CLIENT_ID = 'b61613f8-0da8-4be7-81aa-1c89f2c0fe9f'
    SCOPES = ('https://auth.globus.org/scopes/'
              'identifiers.globus.org/create_update',)
    CONFIG = os.path.expanduser('~/.minid/minid-config.cfg')

    NAME = 'Minid Client'
    NAMESPACE = 'kHAAfCby2zdn'
    TEST_NAMESPACE = 'HHxPIZaVDh9u'

    def __init__(self, *args, **kwargs):
        storage = ConfigParserTokenStorage(filename=self.CONFIG,
                                           section='tokens')
        kwargs.update({
            'app_name': self.NAME,
            'client_id': self.CLIENT_ID,
            'default_scopes': self.SCOPES,
            'token_storage': storage or kwargs.get('token_storage')
        })
        super(MinidClient, self).__init__(*args, **kwargs)

    @property
    def identifiers_client(self):
        try:
            authorizer = self.get_authorizers()['identifiers.globus.org']
        except LoadError:
            authorizer = None
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
