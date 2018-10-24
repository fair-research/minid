import os
import sys
import logging
import json


if sys.version_info > (3,):
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.minid')
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_PATH, 'minid-config.cfg')


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


def parse_config(config_file=DEFAULT_CONFIG_FILE):
    global _config
    if _config:
        return _config
    if config_file == DEFAULT_CONFIG_FILE and not os.path.isfile(config_file):
        logger.info("No default configuration file found, creating one")
        create_default_config()
    _config = ConfigParser()
    _config.read(config_file)
    return _config

def save_tokens(token_dict):
    serialized_tokens = json.dumps(token_dict)
    config = parse_config()
    if 'globus' not in config.sections():
        config.add_section('globus')
    config.set('globus', 'tokens', serialized_tokens)
    with open(DEFAULT_CONFIG_FILE, 'w+') as fh:
        config.write(fh)

def load_tokens():
    config = parse_config()

    serialized_tokens = config.get('globus', 'tokens')
    return json.loads(serialized_tokens)

_config = None