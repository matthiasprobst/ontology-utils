"""Ontolutils package."""
import logging

from ._cfg import set_config, get_config
from ._version import __version__
from .classes import Thing, get_urirefs, get_namespaces, as_id, build, Property
from .classes import namespaces, urirefs
from .classes import query, dquery
from .classes.utils import merge_jsonld
from .namespacelib import *
from .utils.qudt_units import parse_unit

DEFAULT_LOGGING_LEVEL = logging.WARNING
_formatter = logging.Formatter(
    '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S'
)
logger = logging.getLogger('ontolutils')
_sh = logging.StreamHandler()
_sh.setFormatter(_formatter)
logger.addHandler(_sh)


def set_logging_level(level: str):
    """Set the logging level for the package and all its handlers."""
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
           'dquery',
           'get_urirefs',
           'get_namespaces',
           'parse_unit',
           'as_id',
           'build',
           'Property'
           ]
