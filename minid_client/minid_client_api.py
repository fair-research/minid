import sys
import os
import requests
import logging
import hashlib
import json
from collections import OrderedDict

if sys.version_info > (3,):
    from configparser import ConfigParser, NoSectionError
else:
    from ConfigParser import ConfigParser, NoSectionError

# Hardcoded Native Globus Client ID for this client
GLOBUS_CLIENT_ID = 'ff8af9b7-9893-44c7-8634-ebb61a4a692f'
GLOBUS_SCOPES = ['https://auth.globus.org/scopes/a5cdede9-567f-4ae5-aba5-cb997d08693a/minid']

try:
    import globus_sdk
    GLOBUS_AUTH_ENABLED = True
except ImportError:
    GLOBUS_AUTH_ENABLED = False

# Get input method on python 2/3 for globus auth
get_input = getattr(__builtins__, 'raw_input', input)

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.minid')
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_PATH, 'minid-config.cfg')

logger = logging.getLogger(__name__)


def configure_logging(level=logging.INFO, logpath=None):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    # Quiet the Globus SDK
    logging.getLogger("globus_sdk").setLevel(logging.WARNING)
    if logpath:
        logging.basicConfig(filename=logpath, level=level, format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)


def parse_config(config_file):
    if config_file == DEFAULT_CONFIG_FILE and not os.path.isfile(config_file):
        logger.info("No default configuration file found, creating one")
        create_default_config()
    config = ConfigParser()
    config.read(config_file)
    return dict(config.items('general'))


def create_default_config():
    if not os.path.isdir(DEFAULT_CONFIG_PATH):
        os.makedirs(DEFAULT_CONFIG_PATH)
    with open(DEFAULT_CONFIG_FILE, 'w') as config_file:
        config_file.writelines(['[general]\n',
                                'minid_server: http://minid.bd2k.org/minid\n',
                                'email: \n',
                                'orcid: \n',
                                'code: \n'])
    config_file.close()


def globus_auth(login=True):
    """
    Login using Globus Credentials. Supports both cached tokens and fresh
    logins.

    It will exit with an error if the globus_sdk is not installed.

    :param login: Do a login instead of using cached toknes
    :return: A globus access_token for the minid server, or None
    """

    if not login:
        config = ConfigParser()
        config.read(DEFAULT_CONFIG_FILE)
        try:
            if config.get('globus', 'access_token'):
                return config.get('globus', 'access_token')
        except NoSectionError:
            return None

    if not GLOBUS_AUTH_ENABLED:
        print('"globus-sdk" is not installed, you can install it with '
              '"pip install globus-sdk"')
        sys.exit(-1)

    client = globus_sdk.NativeAppAuthClient(GLOBUS_CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=GLOBUS_SCOPES)
    authorize_url = client.oauth2_get_authorize_url()
    print('Visit the URL below: \n{}'.format(authorize_url))
    auth_code = get_input('Please enter the code you '
                          'get after login here: ').strip()

    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    tokens = token_response.by_resource_server
    minid_at = tokens['f238f634-6df8-414d-b3ea-77f2062f0c71']['access_token']
    print('Add the following section to {} for future requests:'
          '\n[globus]\naccess_token = {}\n\n'
          ''.format(DEFAULT_CONFIG_PATH, minid_at))
    return minid_at


def compute_checksum(file_path, algorithm=None, block_size=65536):
    logger.info("Computing checksum for %s using %s" % (file_path, algorithm))
    
    if not algorithm:
        print("creating algorithm")
        algorithm = hashlib.sha256()

    with open(os.path.abspath(file_path), 'rb') as open_file:
        buf = open_file.read(block_size)
        while len(buf) > 0:
            algorithm.update(buf)
            buf = open_file.read(block_size)
    open_file.close()
    return algorithm.hexdigest()


def get_entities(server, name, test):
    logger.info("Checking if the %sentity %s already exists on the server: %s" %
                ("TEST " if test else "", name, server))
    query = ""
    if test:
        query = "?test=true"

    # TODO: this can likely be undone once the server supports "minid:xyz" resolution
    if name.startswith("minid:"):
        name = name.replace("minid:", "ark:/57799/")

    r = requests.get("%s/%s%s" % (server, name, query), headers={"Accept": "application/json"})
    if r.status_code == 404:
        return None
    return r.json()


def create_entity(server, entity, globus_auth_token=None):
    headers = {"Accept": "application/json"}
    if globus_auth_token is not None:
        headers.update({"Authorization": "Bearer " + globus_auth_token})
    r = requests.post(server, json=entity, headers=headers)
    if r.status_code in [200, 201]:
        return r.json()
    elif r.status_code in [401, 403, 500]:
        raise MinidAPIException('Failed to create entity', code=r.status_code, **r.json())
    else:
        logger.error("Error creating entity (%s) -- check parameters or config file for invalid values" % r.status_code)


def entity_json(email, code, checksum, checksum_function, locations, title, test, content_key):
    entity = {"email":  email, "code": code, "checksum": checksum}
    if checksum_function:
        entity["checksum_function"] = checksum_function
    if test:
        entity["test"] = test
    if locations:
        entity["locations"] = locations
    if title: 
        entity["title"] = title
    if content_key:
        entity["content_key"] = content_key
    return entity


def print_entity(entity, as_json):
    if as_json:
        print(json.dumps(entity))
    else:
        print("Identifier: %s" % entity["identifier"])
        print("Created by: %s (%s)" % (entity["creator"], entity["orcid"]))
        print("Created: %s" % entity["created"])
        print("Checksum: %s" % entity["checksum"])

        if entity["content_key"]:
            print("Content Key: %s" % entity["content_key"])

        print("Status: %s" % entity["status"])
        if entity["obsoleted_by"]:
            print("Obsoleted by: %s" % entity["obsoleted_by"])
        print("Locations:")
        for l in entity["locations"]:
            print("  %s - %s" % (l["creator"], l["uri"]))
        print("Title:")
        for t in entity["titles"]:
            print("  %s - %s" % (t["creator"], t["title"]))


def print_entities(entities, as_json):
    for i, entity in entities.items():
        print_entity(entity, as_json)
        print("\n")


def register_user(server, email, name, orcid, globus_auth_token=None):
    logger.info("Registering new user \"%s\" with email \"%s\"%s" %
                (name, email, format(" and orcid \"%s\"" % orcid) if orcid else ""))
    user = {"name": name, "email": email}
    headers = {"Content-Type": "application/json"}
    if globus_auth_token is not None:
        headers.update({"Authorization": "Bearer " + globus_auth_token})
    if orcid:
        user["orcid"] = orcid
    r = requests.post("%s/user" % server, json=user, headers=headers)
    if r.status_code in [401, 403, 500]:
        raise MinidAPIException('Failed to register user', code=r.status_code, **r.json())
    else:
        return r.json()


def register_entity(server, checksum, email, code,
                    url=None, title='', test=False, content_key=None,
                    globus_auth_token=None, checksum_function=None):
    logger.info("Creating new identifier")

    result = create_entity(server,
                           entity_json(email, code, checksum, checksum_function, url, title, test, content_key),
                           globus_auth_token)

    if result:
        logger.info("Created/updated minid: %s" % result["identifier"])
        return result["identifier"]


def register_entities(server, email, code, entity_manifest,
                      test=False, content_key=None, globus_auth_token=None):
    results = list()
    md5_func = "md5"
    sha256_func = "sha256"
    with open(entity_manifest, "r") as manifest:
        line = manifest.readline().lstrip()
        manifest.seek(0)
        is_json_stream = False
        if line.startswith('{'):
            entities = manifest
            is_json_stream = True
        else:
            entities = json.load(manifest, object_pairs_hook=OrderedDict)

        for entity in entities:
            if is_json_stream:
                entity = json.loads(entity, object_pairs_hook=OrderedDict)

            url = entity['url']
            filename = entity['filename']
            metadata = entity.get("metadata", {})
            title = metadata.get("title", os.path.basename(filename))
            md5 = entity.get(md5_func)
            sha256 = entity.get(sha256_func)
            if sha256:
                checksum = sha256
                checksum_function = sha256_func.upper()
            else:
                checksum = md5
                checksum_function = md5_func.upper()
            entities = get_entities(server, checksum, test)
            if entities:
                logging.warning("Entity already registered with checksum: %s" % checksum)
                continue
            result = register_entity(server, checksum, email, code,
                                     [url], title, test, content_key, globus_auth_token, checksum_function)
            entity['url'] = result
            results.append(entity)

        return results


def update_entity(server, name, entity, email, code, globus_auth_token=None):
    if not entity:
        logger.info("No entity found to update")
        return None

    entity['email'] = email
    entity['code'] = code
    headers = {"Accept": "application/json"}
    if globus_auth_token is not None:
        headers["Authorization"] = "Bearer " + globus_auth_token

    r = requests.put("%s/%s" % (server, name), json=entity, headers=headers)

    if r.status_code in [200, 201]:
        return r.json()
    if r.status_code in [401, 403, 500]:
        raise MinidAPIException('Failed to update entity', code=r.status_code, **r.json())
    else:
        logger.error("Error updating entity (%s, %s) -- check parameters or config file for invalid values" % (
            r.status_code, r.text))


class MinidAPIException(Exception):
    def __init__(self, error, message='', code='NA', type='Uncategorized', user=None):
        logger.error("%s (%s - %s): %s" %
                     (error, code, type, message))
        super(MinidAPIException, self).__init__(message)
        self.error = error
        self.message = message
        self.user = user
        self.code = code
        self.type = type
