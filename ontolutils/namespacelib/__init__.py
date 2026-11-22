"""Curated namespace exports; namespace generation is an explicit developer operation."""
from importlib import import_module as _import_module

from ._iana_utils import IANA
from .codemeta import CODEMETA
from .m4i import M4I
from .obo import OBO
from .qudt_kind import QUDT_KIND
from .qudt_unit import QUDT_UNIT
from .schema import SCHEMA
from .hdf5 import HDF5
from .spdx import SPDX
from .ssn_system import SSN_SYSTEM


__all__ = ['IANA', 'CODEMETA', 'M4I', 'OBO', 'QUDT_KIND', 'QUDT_UNIT',
           'SCHEMA', 'HDF5', 'SPDX', 'SSN_SYSTEM']


def __getattr__(name):
    """Keep explicit developer-tool access without importing generators at startup."""
    if name == '__dev':
        module = _import_module(f'{__name__}.__dev')
        globals()[name] = module
        return module
    raise AttributeError(f'Module {__name__!r} has no attribute {name!r}')
