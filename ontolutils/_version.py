"""Version library for ontolutils package. Determines the version of the package."""
try:
    from importlib.metadata import version as _version
except ImportError as e:
    raise ImportError('Most likely you have python<3.9 installed. At least 3.9 is required.') from e

__version__ = _version('ontolutils')
