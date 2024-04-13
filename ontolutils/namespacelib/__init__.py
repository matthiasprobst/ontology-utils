"""Auto-generated file. Do not edit!"""
import sys

import requests

from . import __dev
from ._iana_utils import IANA
from .codemeta import CODEMETA
from .m4i import M4I
from .obo import OBO
from .qudt_kind import QUDT_KIND
from .qudt_unit import QUDT_UNIT
from .schema import SCHEMA
from .ssno import SSNO
from ..cache import package_user_dir

# create pivmeta module in local user directory
try:
    __dev.pivmeta(filename=package_user_dir / 'pivmeta.py')
except requests.exceptions.ConnectionError:
    pass  # no internet connection, the pivmeta module may not be up to date

sys.path.insert(0, str(package_user_dir))

# noinspection PyUnresolvedReferences
from pivmeta import PIVMETA

assert PIVMETA._NS == 'https://matthiasprobst.github.io/pivmeta#'
