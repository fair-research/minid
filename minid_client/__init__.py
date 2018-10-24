import logging
__VERSION__ = '2.0.0-dev0'


def configure_logging(level=logging.INFO, logpath=None):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if logpath:
        logging.basicConfig(filename=logpath, level=level, format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)
