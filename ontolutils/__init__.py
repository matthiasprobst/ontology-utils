import logging

from ._version import __version__
from .classes import Thing
from .classes import namespaces, urirefs
from .classes import query, dquery
from .classes.utils import merge_jsonld
from .namespacelib import *

DEFAULT_LOGGING_LEVEL = logging.WARNING
logging.basicConfig()
logger = logging.getLogger(__package__)
_sh = logging.StreamHandler()
logger.addHandler(_sh)


def set_logging_level(level: str):
    logger.setLevel(level)
    for h in logger.handlers:
        h.setLevel(level)


set_logging_level(DEFAULT_LOGGING_LEVEL)

__all__ = ['Thing',
           '__version__',
           'namespaces',
           'urirefs',
           'query',
           'set_logging_level',
           'merge_jsonld',
           ]
