import logging

from minid.auth import login, logout
from minid.config import config
from minid.api import MinidClient


def configure_logging(level=logging.INFO, logpath=None):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if logpath:
        logging.basicConfig(filename=logpath, level=level, format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)


# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library  # noqa
logging.getLogger('minid').addHandler(logging.NullHandler())

__all__ = [

    'login', 'logout',

    'config',

    'MinidClient',
]
