import warnings

from . import Attribution

warnings.warn("Module 'ontolutils.ex.prov.attribution' is deprecated, use 'ontolutils.ex.prov.Attribution' instead.",
              DeprecationWarning, stacklevel=2)

__all__ = ['Attribution']
