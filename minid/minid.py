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
import datetime

import fair_research_login
import globus_sdk
from fair_identifiers_client.identifiers_api import IdentifierClient
from fair_identifiers_client.main import SUPPORTED_CHECKSUMS
from minid.exc import MinidException, LoginRequired, UnknownIdentifier
log = logging.getLogger(__name__)


class MinidClient(object):
    CLIENT_ID = 'fa63f71e-4b8c-4032-b78e-0fc6214efd0b'
    SCOPES = ('https://auth.globus.org/scopes/identifiers.fair-research.org/'
              'writer', 'openid', 'profile')
    CONFIG = os.path.expanduser('~/.minid/minid-config.cfg')

    NAME = 'Minid Client'
    # The namespaces within the identifiers.fair-research.org service
    IDENTIFIERS_NAMESPACE = 'minid'
    IDENTIFIERS_NAMESPACE_TEST = 'minid-test'

    # Common prefixes associated with MINID
    PREFIXES = {
        'minid': 'minid:',
        'hdl': 'hdl:20.500.12582/',
        'ark': 'ark:/57799/',
    }
    PREFIXES_TEST = {
        'minid': 'minid.test:',
        'hdl': 'hdl:20.500.12633/',
        'ark': 'ark:/99999/',
    }

    def __init__(self, authorizer=None, app_name=None, native_client=None,
                 config=None,
                 base_url='https://identifiers.fair-research.org/'):
        self.app_name = app_name or self.NAME
        self.config = config or self.CONFIG
        self.base_url = base_url
        self._authorizer = authorizer
        self._identifiers_client = None

        config_dir = os.path.dirname(self.config)
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

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
            return self.native_client.get_authorizers_by_scope()[
                'https://auth.globus.org/scopes/identifiers.fair-research.org/'
                'writer'
            ]
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
        if not self._identifiers_client:
            self._identifiers_client = IdentifierClient(
                base_url=self.base_url,
                app_name=self.app_name,
                authorizer=self.authorizer
            )
        return self._identifiers_client

    def get_cached_created_by(self):
        """Get the 'created_by' field by pulling the current users name from
        Globus Auth. The field is only fetched the first time after the client
        has been instantiated. After that, the value is cached and returned
        from memory. This speeds things up if calling register() multiple times
        from the same client.
        """
        if getattr(self, '_cached_created_by', None):
            return self._cached_created_by
        authorizer = self.native_client.get_authorizers()['auth.globus.org']
        ac = globus_sdk.AuthClient(authorizer=authorizer)
        user_info = ac.oauth2_userinfo()
        self._cached_created_by = user_info.data.get('name', '')
        return self._cached_created_by

    def register_file(self, filename, title='', locations=None, test=False,
                      replaces=None):
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
          ``replaces`` (* string *)
          ID of another identifier to replace
        ** Returns **
        A dict describing attributes of the identifier.
        See ``register`` for an example of the output.
        """
        if not self.is_logged_in():
            raise LoginRequired('The Minid Client did not have a valid '
                                'authorizer.')
        locations = locations or []
        title = title or filename
        metadata = {
            'title': title or filename,
            'length': os.path.getsize(filename),
            'created_by': self.get_cached_created_by(),
        }
        checksums = [{
            'function': 'sha256',
            'value': self.compute_checksum(filename, hashlib.sha256())
        }]
        return self.register(checksums, title=title, locations=locations,
                             test=test, metadata=metadata, replaces=replaces)

    def register(self, checksums, title='', locations=None, test=False,
                 metadata=None, **kwargs):
        """Register pre-prepared data, where the checksum already exists for
        a given file.
        ** Parameters **
          ``checksums`` (*list of dicts*)
          A list of dicts containing checksums. Example:
          [{'function': 'sha256', 'value': 'computed sha256 checksum'},]
          ``title`` (* string *)
          The title used to refer to the minid. Defaults to filename
          ``locations`` (* array of strings *)
          Network accessible locations for the given file
          ``test`` (* boolean *)
          Create the minid in a non-permanent test namespace
          ``metadata`` (* dict *)
          A dictionary containing extra metadata about the identifier. 'title'
          is set by given ``title`` and created_by is by default the logged-in
          user.
          ``replaces`` (* string *)
          ID of another identifier to replace
        ** Returns **
        A Dict describing the identifier. Example:
        {
          "active": true,
          "admins": ['identities-of-admins'],
          "checksums": [
            {
              "function": "sha256",
              "value": "checksum"
            }
          ],
          "created": "2020-04-08T14:17:53.212592",
          "identifier": "hdl:20.500.12633/1234567",
          "landing_page": "https://identifiers.fair-research.org/minid",
          "location": [],
          "metadata": {
            "created_by": "The Creator",
            "length": 76,
            "title": "foo.txt"
          },
          "replaced_by": "hdl:20.500.12633/456",
          "replaces": "hdl:20.500.12633/789",
          "updated": "2020-04-08T15:26:25.256145",
          "visible_to": [
            "public"
          ]
        }
        """
        if not self.is_logged_in():
            raise LoginRequired('The Minid Client did not have a valid '
                                'authorizer.')
        locations = locations or []
        unsupported = [c for c in checksums
                       if c['function'] not in SUPPORTED_CHECKSUMS]
        if unsupported:
            log.warning('The following checksums for {} are unsupported and '
                        'will not be included: {}'.format(title,
                                                          unsupported))
        supported_ck = [c for c in checksums
                        if c['function'] in SUPPORTED_CHECKSUMS]
        metadata = metadata or {}
        metadata['title'] = title
        namespace = (self.IDENTIFIERS_NAMESPACE_TEST if test is True
                     else self.IDENTIFIERS_NAMESPACE)
        if kwargs.get('replaces'):
            kwargs['replaces'] = self.to_identifier(kwargs['replaces'],
                                                    identifier_type='hdl')
        return self.identifiers_client.create_identifier(
            namespace=namespace,
            visible_to=['public'],
            metadata=metadata,
            location=locations,
            checksums=supported_ck,
            **kwargs
        )

    def update(self, minid, title=None, **kwargs):
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
          ``active`` (*boolean*)
          Set the state to active or not. The state will only change if the
          ``active`` value is passed as true or false, not including this arg
          will leave it the same.
          ``replaces`` (*string*)
          The id of the identifier which this identifier replaces. None will
          clear an existing `replaces` value.
          ``replaced_by`` (*string*)
          The id of the identifier that replaces this identifier. None will
          clear an existing `replaces` value.
        """
        allowed_kwargs = {'title', 'locations', 'metadata', 'active',
                          'replaces', 'replaced_by'}
        if not set(kwargs).issubset(allowed_kwargs):
            raise MinidException('Update args not allowed: {}'.format(
                set(kwargs).difference(allowed_kwargs)
            ))
        if not self.is_logged_in():
            raise LoginRequired('The Minid Client did not have a valid '
                                'authorizer.')
        # Ensure metadata is set, even if it doesn't have anything in it.
        kwargs['metadata'] = kwargs.get('metadata', {})
        # Set title if it is given
        if title:
            kwargs['metadata']['title'] = title
        identifier = self.to_identifier(minid, identifier_type='hdl')
        for ent in kwargs:
            if ent in ['replaces', 'replaced_by']:
                # 'replaces' or 'replaced_by' MUST be either a vaild identifier
                # or None to unset. to_identifier() will raise an exception if
                # the identifier cannot resolve to hdl.
                value = None if kwargs[ent] is None else self.to_identifier(
                    kwargs[ent], identifier_type='hdl')
                kwargs[ent] = value
        # The 'location' field in the service is not plural
        if 'locations' in kwargs.keys():
            kwargs['location'] = kwargs.pop('locations')
        return self.identifiers_client.update_identifier(
            identifier, **kwargs)

    def check(self, entity, algorithm='sha256'):
        """
        ** Parameters **
          ``entity`` (*string*)
          entity can either be a filename or a minid. If the entity stars
          with 'ark:/' it will be treated as a minid. Otherwise, it will
          be treated as a file.
          ``algorithm`` (*string*)
          If the entity given is a file, it will be automatically checksummed
          with the algorithm given. The algorithm must be in the hashlib
          python library and be supported by the Identifiers Service (all
          common algorithms in the hashlib module are supported).
        """
        if self.is_valid_identifier(entity):
            hdl = self.to_identifier(entity, 'hdl')
            return self.identifiers_client.get_identifier(hdl)
        else:
            alg = self.get_algorithm(algorithm)
            checksum = self.compute_checksum(entity, alg)
            log.debug('File lookup using ({}) {}'.format(algorithm, checksum))
            return self.identifiers_client.get_identifier_by_checksum(checksum)

    @staticmethod
    def _is_stream(file_handle):
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

    @classmethod
    def read_manifest_entries(cls, manifest_filename):
        """
        Read a given filename and yield each entity in the manifest until
        there are no more manifests. Works if the manifest_filename is a stream
        or a regular file.

        """
        with open(manifest_filename, 'r') as manifest:
            is_stream = cls._is_stream(manifest)
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

    def register_rfm(self, rfm_record, test, update_if_exists=False):
        """
        Register a Minid for a given rfm record. Records will always be
        re-registered unless `update_if_exists` is True.
        ** Parameters **
          ``rfm_record`` (*dict*)
            A single record within a remote_file_manifest. The record must be a
            dict with at least 'filename', 'url' and at least one
            hash algorithm. 'md5' and 'sha256' are common, but anything in
            python hashlib should work too.
          ``test`` (*boolean*)
            Register using a minid test namespace
          ``update_if_exists`` (*bool*) Default False. Attempt to keep an
            existing minid if one exists and the checksum matches. Otherwise
            re-register and replace the existing minid.
        ** Returns **
            A dict with 'url' replaced with the registered identifier
        ** Example **
        # Calling with a single RFM Record, with test=True to register as test:
        register_rfm({
                "url": "https://example.com/foo.txt",
                "sha256": "6e3fbc3cc8c58edd0d99cd4925d18cdbd7ffbfa1a7fb201c06",
                "filename": "foo.txt"
            },
            True
        )
        # Returns the following:
          {
            "url": "hdl:20.500.12633/07ace189c3d6",
            "sha256": "6e3fbc3cc8c58edd0d99cd4925d18cdbd7ffbfa1a7fb201c06",
            "filename": "foo.txt"
          }
        """
        checksums = [{'function': f, 'value': rfm_record.get(f)}
                     for f in SUPPORTED_CHECKSUMS
                     if f in rfm_record.keys()]
        locations = (rfm_record['url']
                     if isinstance(rfm_record['url'], list)
                     else [rfm_record['url']]
                     )
        is_valid = self.is_valid_identifier(rfm_record['url'])
        matches_namespace = self.is_test(rfm_record['url']) is test
        log.debug('{}, URL is minid: {}, matches namespace: {}'
                  ''.format(rfm_record['url'], is_valid, matches_namespace))
        if update_if_exists and is_valid and matches_namespace:
            existing_minid = self.check(rfm_record['url']).data
            # Update the existing minids locations if it exists
            if existing_minid and self.validate_checksums(
                    existing_minid['checksums'], checksums):
                m_resp = self.update(rfm_record['url'],
                                     title=rfm_record['filename'],
                                     locations=locations).data
                log.info('Updating existing minid {} for filename {}'
                         ''.format(rfm_record['url'], rfm_record['filename']))
            # Otherwise, re-register and replace the the existing minid
            else:
                m_resp = self.register(checksums, test=test,
                                       locations=locations,
                                       title=rfm_record['filename'],
                                       replaces=rfm_record['url'])
                log.info('re-registered existing minid {} with {} for filename'
                         ' {}'.format(rfm_record['url'], m_resp['identifier'],
                                      rfm_record['filename']))

        else:
            m_resp = self.register(checksums, test=test, locations=locations,
                                   title=rfm_record['filename']).data
            log.info('Replaced {} with minid'.format(rfm_record['url']))
        new_manifest = rfm_record.copy()
        new_manifest['url'] = m_resp['identifier']
        return new_manifest

    def batch_register(self, manifest_filename, test, update_if_exists=False):
        """
        Register All entries within a remote file manifest, and replace the
        'url' on each record with an identifier. Existing identifiers will
        be re-registered and replaced with a new identifier. update_if_exists
        will attempt to keep the same identifier if the checksum matches the
        original, in which it will update the old minids information.

        The manifest must conform to the bdbag spec laid out here:
        https://github.com/fair-research/bdbag/blob/master/doc/config.md#remote-file-manifest  # noqa
        ** Parameters **
          ``manifest_filename`` (*string*) The filename to a remote file
            manifest. The file may either be a real file or a streamed file. If
            it is a streamed file, each record must be encapsulated within each
            line of the manifest.
          ``test`` (*bool*) Register in the temporary test namespace, or the
            permanent production namespace. Records are not re-registered if
            one already exists.
          ``update_if_exists`` (*bool*) Default False. Attempt to keep an
            existing minid if one exists and the checksum matches. Otherwise
            re-register and replace the existing minid.
        ** Returns **
          A list of records with 'url' field replaced with the identifier. See
          get_or_register_rfm() above for more details.
        """
        log.info("Processing batch registrations...")
        start = datetime.datetime.now()
        results = [self.register_rfm(record, test,
                                     update_if_exists=update_if_exists)
                   for record in self.read_manifest_entries(manifest_filename)]
        elapsed = datetime.datetime.now() - start
        log.info("Batch register processed {} entries in {}".format(len(results), elapsed))
        return results

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
    def validate_checksums(checksums1, checksums2):
        by_key1 = {c['function']: c['value'] for c in checksums1}
        by_key2 = {c['function']: c['value'] for c in checksums2}
        common_algorithms = set(by_key1) & set(by_key2)
        if not common_algorithms:
            return False

        return all(by_key1[alg] == by_key2[alg] for alg in common_algorithms)

    @staticmethod
    def compute_checksum(file_path, algorithm=None, block_size=65536):
        if not algorithm:
            algorithm = hashlib.sha256()
            log.debug("Using hash algorithm: {}".format(algorithm))
        if os.path.isdir(file_path):
            raise MinidException(f'Directories are not supported by Minid: {file_path}')

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

    @classmethod
    def is_valid_identifier(cls, identifier):
        """Returns True if the identifier is known and can be resolved by Minid
        """
        return bool(cls.get_identifier_prefix(identifier))

    @classmethod
    def is_minid(cls, entity):
        """Returns True if entity is a minid, False otherwise"""
        if not isinstance(entity, str):
            return False
        return bool(entity.startswith(cls.PREFIXES['minid']) or entity.startswith(cls.PREFIXES_TEST['minid']))

    @classmethod
    def get_identifier_prefix(cls, identifier):
        """Returns the prefix for the given identifier. Checks in both the
        normal prefixes and the test prefixes.
        ** Parameters **
          ``identifier`` (*string*) A Minid compatible identifier. Ex:
          minid:foobarbaz
        ** Returns **
        The prefix for the given identifer. Examples
          * "minid:"
          * "minid.test:"
          * "hdl:20.500.12633"
          * "hld:20.500.12582"
        """
        prefixes = (list(cls.PREFIXES.values()) +
                    list(cls.PREFIXES_TEST.values()))
        prefix = list(filter(lambda pfx: identifier.startswith(pfx), prefixes))
        return prefix[0] if prefix else None

    @classmethod
    def is_test(cls, identifier):
        """Returns true if the identifier exists within the test namespace"""
        return any([identifier.startswith(idpx)
                    for idpx in cls.PREFIXES_TEST.values()])

    @classmethod
    def to_identifier(cls, identifier, identifier_type='hdl'):
        """Returns the prefix for the given identifier. Checks in both the
        normal prefixes and the test prefixes.
        ** Parameters **
          ``identifier`` (*string*) A Minid compatible identifier. Ex:
          minid:foobarbaz
          ``identifier_type`` (*string*) The preferred type of identifier to
          translate the given *identifier*.
        ** Returns **
        The translated identifier as a string type. Examples:
          * "minid:foobarbaz"
          * "minid.test:foobarbaz"
          * "hdl:20.500.12633/foobarbaz"
          * "hld:20.500.12582/foobarbaz"
        """
        if identifier_type not in cls.PREFIXES:
            raise UnknownIdentifier(f'Identifier type "{identifier_type}" is not supported by Minid.')
        prefix = cls.get_identifier_prefix(identifier)
        if prefix is None:
            raise UnknownIdentifier(f'Given identifier "{identifier}" is not supported by Minid.')
        if cls.is_test(identifier):
            identifier_prefix = cls.PREFIXES_TEST[identifier_type]
        else:
            identifier_prefix = cls.PREFIXES[identifier_type]
        return identifier.replace(prefix, identifier_prefix)

    @classmethod
    def to_minid(cls, identifier):
        """Convenience method. Calls (to_identifier(identifier, 'minid').
        Returns the given identifier as a Minid.
        """
        return cls.to_identifier(identifier, identifier_type='minid')
