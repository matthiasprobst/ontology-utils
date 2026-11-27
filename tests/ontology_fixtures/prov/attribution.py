import warnings

from . import Attribution

warnings.warn("Module 'ontology_fixtures.prov.attribution' is deprecated, use 'ontology_fixtures.prov.Attribution' instead.",
              DeprecationWarning, stacklevel=2)

__all__ = ['Attribution']
