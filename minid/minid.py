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
import json
from collections import OrderedDict
import hashlib

import fair_research_login
from identifiers_client.identifiers_api import IdentifierClient
from identifiers_client.main import SUPPORTED_CHECKSUMS
from minid.exc import MinidException, LoginRequired

log = logging.getLogger(__name__)


class MinidClient(object):
    CLIENT_ID = 'fa63f71e-4b8c-4032-b78e-0fc6214efd0b'
    SCOPES = ('https://auth.globus.org/scopes/identifiers.fair-research.org/'
              'writer')
    CONFIG = os.path.expanduser('~/.minid/minid-config.cfg')

    NAME = 'Minid Client'
    NAMESPACE = 'minid'
    TEST_NAMESPACE = 'minid-test'
    MINID_PREFIX = 'hdl:'

    def __init__(self, authorizer=None, app_name=None, native_client=None,
                 config=None,
                 base_url='https://identifiers.fair-research.org/'):
        self.app_name = app_name or self.NAME
        self.config = config or self.CONFIG
        self.base_url = base_url
        self._authorizer = authorizer

        if native_client is None:
            storage = fair_research_login.ConfigParserTokenStorage(
                filename=self.config, section='tokens')
            self.native_client = fair_research_login.NativeClient(
                app_name=self.app_name, client_id=self.CLIENT_ID,
                default_scopes=self.SCOPES, token_storage=storage
            )

    def login(self, refresh_tokens=False, no_local_server=True,
              no_browser=True, force=False):
        """
        Authenticate with Globus for tokens to talk to the remote Identifiers
        Server. Login is only needed for some operations, reading identifiers
        can be done anonymously.
        **Parameters**
        ``no_local_server`` (*bool*)
          Disable spinning up a local server to automatically copy-paste the
          auth code. THIS IS REQUIRED if you are on a remote server, as this
          package isn't able to determine the domain of a remote service. When
          used locally with no_local_server=False, the domain is localhost with
          a randomly chosen open port number. Typically not used when calling
          directly into a client.
        ``no_browser`` (*string*)
          Do not automatically open the browser for the Globus Auth URL.
          Display the URL instead and let the user navigate to that location.
          This usually isn't desired if calling from a jupyter notebook or from
          a remote server.
        ``refresh_tokens`` (*bool*)
          Ask for Globus Refresh Tokens to extend login time.
        ``force`` (*bool*)
          Force a login flow, even if loaded tokens are valid.
        """
        self.native_client.login(refresh_tokens=refresh_tokens,
                                 no_local_server=no_local_server,
                                 no_browser=no_browser,
                                 force=force)

    def logout(self):
        """
        Revoke local tokens and clear the token cache.
        """
        try:
            self.native_client.load_tokens()
            self.native_client.logout()
            return True
        except fair_research_login.LoadError:
            return False

    @property
    def authorizer(self):
        if self._authorizer is not None:
            return self._authorizer
        try:
            return self.native_client.get_authorizers_by_scope()[self.SCOPES]
        except fair_research_login.LoadError:
            return None

    @authorizer.setter
    def authorizer(self, value):
        self._authorizer = value

    def is_logged_in(self):
        return bool(self.authorizer)

    @property
    def identifiers_client(self):
        log.debug('Authorizer: {}'.format(self.authorizer))
        return IdentifierClient(
            base_url=self.base_url,
            app_name=self.app_name,
            authorizer=self.authorizer
        )

    def is_minid(self, entity):
        """Returns True if entity is a minid, False otherwise"""
        return isinstance(entity, str) and entity.startswith(self.MINID_PREFIX)

    def register_file(self, filename, title='', locations=None, test=False):
        """
        Register a file and produce an identifier. The file is automatically
        checksummed using sha256, and the checksum is sent to the identifiers
        service along with any other metadata. The hash can later be looked up
        using the ``check()`` command.
        ** Parameters **
          ``filename`` (*string*)
          The filename used to create a minid
          ``title`` (* string *)
          The title used to refer to the minid. Defaults to filename
          ``locations`` (* array of strings *)
          Network accessible locations for the given file
          ``test`` (* boolean *)
          Create the minid in a non-permanent test namespace
        ** Returns **

        """
        metadata = {
            '_profile': 'erc',
            'erc.what': title or filename
        }
        checksums = [{
            'function': 'sha256',
            'value': self.compute_checksum(filename, hashlib.sha256())
        }]
        return self.register(checksums, title=title, locations=locations,
                             test=test, metadata=metadata)

    def register(self, checksums, title='', locations=None, test=False,
                 metadata=None):
        """Register pre-prepared data, where the checksum already exists for
        a given file."""
        if not self.is_logged_in():
            raise LoginRequired('The Minid Client did not have a valid '
                                'authorizer.')
        unsupported = [c for c in checksums
                       if c['function'] not in SUPPORTED_CHECKSUMS]
        if unsupported:
            log.warning('The following checksums for {} are unsupported and '
                        'will not be included: {}'.format(title,
                                                          unsupported))
        metadata = metadata or {}
        metadata['title'] = title
        namespace = self.TEST_NAMESPACE if test is True else self.NAMESPACE
        return self.identifiers_client.create_identifier(namespace=namespace,
                                                         visible_to=['public'],
                                                         metadata=metadata,
                                                         location=locations,
                                                         checksums=checksums
                                                         )

    def update(self, minid, title='', locations=None, metadata=None):
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
        if not self.is_logged_in():
            raise LoginRequired('The Minid Client did not have a valid '
                                'authorizer.')
        locations, metadata = locations or [], metadata or {}
        if title:
            metadata['erc.what'] = title
        return self.identifiers_client.update_identifier(minid,
                                                         metadata=metadata,
                                                         location=locations)

    def check(self, entity, algorithm='sha256'):
        """
        ** Parameters **
          ``entity`` (*string*)
          entity can either be a filename or a minid. If the entity stars
          with 'ark:/' it will be treated as a minid. Otherwise, it will
          be treated as a file.
        """
        if self.is_minid(entity):
            return self.identifiers_client.get_identifier(entity)
        else:
            alg = self.get_algorithm(algorithm)
            checksum = self.compute_checksum(entity, alg)
            log.debug('File lookup using ({}) {}'.format(algorithm, checksum))
            return self.identifiers_client.get_identifier_by_checksum(checksum)

    def get_most_recent_active_entity(self, entities):
        """If there are multiple entities, return the entity with the latest
        timestamp."""
        if len(entities.data['identifiers']) > 0:
            return entities.data['identifiers'][-1]
        return None
        # HACK! Currently the date created is not returned, so we can't get the
        # time for each identifier. Simply return the last one in the list the
        # server generates.
        # active_sorted = sorted(entities,
        #                        key=lambda x: datetime.datetime.strptime(
        #                            x["created"], '%Y-%m-%dT%H:%M:%S.%f'),
        #                        reverse=True)
        # if active_sorted:
        #     return active_sorted[0]

    def _is_stream(self, file_handle):
        """
        Returns true if the given file handle is a stream of remote file
        manifests, false if it is a file.
        """
        line = file_handle.readline().lstrip()
        file_handle.seek(0)
        is_json_stream = False
        if line.startswith('{'):
            is_json_stream = True
        return is_json_stream

    def read_manifest_entries(self, manifest_filename):
        """
        Read a given filename and yield each entity in the manifest until
        there are no more manifests. Works if the manifest_filename is a stream
        or a regular file.
        """
        with open(manifest_filename, 'r') as manifest:
            is_stream = self._is_stream(manifest)
            log.info('Parsing {} from filename {}'
                     ''.format('stream' if is_stream else 'file',
                               manifest_filename)
                     )

            # Fetch 'entities' to iterate upon.
            if not is_stream:
                entities = json.load(manifest, object_pairs_hook=OrderedDict)
            else:
                entities = manifest

            # Iterate over the entities and yield each one until we run out.
            for entity in entities:
                if is_stream:
                    yield json.loads(entity, object_pairs_hook=OrderedDict)
                else:
                    yield entity

    def get_or_register_manifest_entry(self, manifest_entity, test):
        """
        If the entity within the manifest has already been registered, fetch
        the remote entity. If None exists, create a new Minid for the data
        within the manifest entity. Return the 'minid' for the URL.
        """
        log.debug('Checking entry {}'.format(manifest_entity['filename']))
        existing_entities = self.identifiers_client.get_identifier_by_checksum(
            manifest_entity['sha256']
        )
        entity = self.get_most_recent_active_entity(existing_entities)
        if not entity:
            checksums = [{'function': f, 'value': manifest_entity.get(f)}
                         for f in SUPPORTED_CHECKSUMS
                         if f in manifest_entity.keys()]
            locations = (manifest_entity['url']
                         if isinstance(manifest_entity['url'], list)
                         else [manifest_entity['url']]
                         )
            entity = self.register(checksums, test=test, locations=locations,
                                   title=manifest_entity['filename'])
        else:
            log.warning('Entity already registered, using {} for {}.'
                        ''.format(entity['identifier'],
                                  manifest_entity['filename']))
        new_manifest = manifest_entity.copy()
        new_manifest['url'] = entity['identifier']
        return new_manifest

    def batch_register(self, manifest_filename, test):
        return [self.get_or_register_manifest_entry(entry, test)
                for entry in self.read_manifest_entries(manifest_filename)]

    @staticmethod
    def get_algorithm(algorithm_name):
        """
        Get an algorithm from hashlib by str
        :param algorithm_name: Name of the algorithm. Example: 'sha256'
        :return: The hashlib algorithm, or a MinidException if it does not
        exist
        """
        alg = getattr(hashlib, algorithm_name, None)
        if alg is None:
            raise MinidException('Algorithm {} is not available.'
                                 .format(algorithm_name))
        return alg()

    @staticmethod
    def compute_checksum(file_path, algorithm=None, block_size=65536):
        if not algorithm:
            algorithm = hashlib.sha256()
            log.debug("Using hash algorithm: {}".format(algorithm))

        log.debug('Computing checksum for {} using {}'.format(file_path,
                                                              algorithm))
        if not os.path.exists(file_path):
            raise MinidException('File not Found: {}'.format(file_path))

        try:
            with open(os.path.abspath(file_path), 'rb') as open_file:
                buf = open_file.read(block_size)
                while len(buf) > 0:
                    algorithm.update(buf)
                    buf = open_file.read(block_size)
            open_file.close()
            return algorithm.hexdigest()
        except Exception:
            raise MinidException('Unable to checksum file {}'.format(
                file_path)
            )
