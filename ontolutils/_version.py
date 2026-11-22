"""Version library for ontolutils package. Determines the version of the package."""
from importlib.metadata import version as _version

__version__ = _version('ontolutils')
